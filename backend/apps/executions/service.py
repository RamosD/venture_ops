"""Serviço de execuções assistidas: criação com snapshots e contexto (MVP-11).

Concentra as regras de domínio e a transaccionalidade da **criação** (a única
operação de escrita desta pipeline). Congela o contexto no instante da criação:

- captura `function_snapshot` e `product_snapshot` (só campos aprovados);
- resolve `instruction_version` como a `current_version` exacta do documento de
  instruções da função (ou `null`);
- liga **versões documentais exactas** (nunca a versão actual do documento) numa
  ordem determinística e imutável.

Os comandos funcionais (importar/aprovar/rejeitar/corrigir/concluir) **não** são
implementados aqui (F1-P06); consomem a política central em `transitions.py`.
"""
from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from apps.documents.models import DocumentType, DocumentVersion, ExportPolicy
from apps.executions.models import AIExecution, ExecutionContextDocument
from apps.functions.models import FunctionProfile
from apps.portfolio.models import Product


class ExecutionServiceError(Exception):
    """Base dos erros de domínio de execuções."""


class ExecutionNotFound(ExecutionServiceError):
    """Execução inexistente no contexto da empresa (→ 404)."""


class ProductInvalid(ExecutionServiceError):
    """Produto inexistente ou de outra empresa (→ 400)."""


class ProductNotActive(ExecutionServiceError):
    """Produto não está `active` (→ 400)."""


class FunctionInvalid(ExecutionServiceError):
    """Função inexistente ou de outra empresa (→ 400)."""


class FunctionNotActive(ExecutionServiceError):
    """Função não está `active` — não seleccionável em novas execuções (→ 400)."""


class InstructionDocumentDenied(ExecutionServiceError):
    """Documento de instruções com `export_policy=denied` (→ 400)."""


class ContextEmpty(ExecutionServiceError):
    """Nenhuma versão documental de contexto seleccionada (→ 400)."""


class ContextVersionInvalid(ExecutionServiceError):
    """Versão inexistente, de outra empresa ou de outro produto (→ 400)."""


class ContextVersionDenied(ExecutionServiceError):
    """Versão de documento com `export_policy=denied` na selecção (→ 400)."""


class ContextVersionIsInstruction(ExecutionServiceError):
    """A versão de instruções da função não pode ser repetida como dados (→ 400)."""


class ContextDuplicateVersion(ExecutionServiceError):
    """Versão documental repetida na lista de contexto (→ 400)."""


def _resolve_product(product_id, organisation) -> Product:
    product = Product.objects.filter(pk=product_id, organisation=organisation).first()
    if product is None:
        raise ProductInvalid()
    if product.status != Product.Status.ACTIVE:
        raise ProductNotActive()
    return product


def _resolve_function(function_id, organisation) -> FunctionProfile:
    function = FunctionProfile.objects.filter(
        pk=function_id, organisation=organisation
    ).select_related("instruction_document").first()
    if function is None:
        raise FunctionInvalid()
    if function.status != FunctionProfile.Status.ACTIVE:
        raise FunctionNotActive()
    return function


def _build_function_snapshot(function: FunctionProfile) -> dict:
    """Só os campos aprovados da função no instante da criação (imutável)."""
    return {
        "id": str(function.pk),
        "name": function.name,
        "actor_type": function.actor_type,
        "purpose": function.purpose,
        "responsibilities": function.responsibilities,
        "constraints": function.constraints,
        "requires_approval": function.requires_approval,
    }


def _build_product_snapshot(product: Product) -> dict:
    """Dados mínimos da secção Produto do pacote; sem credenciais nem dados pessoais."""
    snapshot = {
        "id": str(product.pk),
        "name": product.name,
        "purpose": product.purpose,
        "status": product.status,
    }
    # Campos opcionais só quando existem (artefacto 04 §2.2).
    if product.phase:
        snapshot["phase"] = product.phase
    if product.target_audience:
        snapshot["target_audience"] = product.target_audience
    return snapshot


def _resolve_instruction_version(function: FunctionProfile) -> DocumentVersion | None:
    """Versão exacta das instruções da função (ou `None`); reavalia a política.

    - sem documento → `None`;
    - com documento: tem de ser `instrucoes`, da mesma empresa, com
      `current_version` válida; se `export_policy=denied`, rejeita a execução.
    """
    document = function.instruction_document
    if document is None:
        return None
    # Defesa em profundidade (a criação da função já validou tipo/empresa/versão).
    if document.document_type != DocumentType.INSTRUCTIONS:
        raise FunctionInvalid()
    if document.organisation_id != function.organisation_id:
        raise FunctionInvalid()
    if document.export_policy == ExportPolicy.DENIED:
        raise InstructionDocumentDenied()
    if document.current_version_id is None:
        raise FunctionInvalid()
    return document.current_version


def _resolve_context_versions(
    *, items, organisation, product, instruction_version
) -> list[tuple[DocumentVersion, str]]:
    """Valida e resolve a lista ordenada de versões de contexto.

    Devolve `[(version, purpose), ...]` na ordem recebida. Valida isolamento,
    coerência de produto, `export_policy`, não repetição da versão de instruções
    e não duplicação. Nunca lê a versão *actual* do documento — usa a versão
    exacta indicada.
    """
    if not items:
        raise ContextEmpty()

    resolved: list[tuple[DocumentVersion, str]] = []
    seen_versions: set = set()
    instruction_version_id = (
        instruction_version.pk if instruction_version is not None else None
    )

    for item in items:
        version_id = item["document_version"]
        if version_id in seen_versions:
            raise ContextDuplicateVersion()
        seen_versions.add(version_id)

        version = (
            DocumentVersion.objects.filter(
                pk=version_id, document__organisation=organisation
            )
            .select_related("document")
            .first()
        )
        if version is None:
            raise ContextVersionInvalid()

        document = version.document
        # Documento empresarial (product null) ou do MESMO produto da execução.
        if document.product_id is not None and document.product_id != product.pk:
            raise ContextVersionInvalid()
        # Política de exportação: `denied` bloqueia a selecção (confirm é aceite).
        if document.export_policy == ExportPolicy.DENIED:
            raise ContextVersionDenied()
        # A versão de instruções da função não é repetida como documento de dados.
        if instruction_version_id is not None and version.pk == instruction_version_id:
            raise ContextVersionIsInstruction()

        resolved.append((version, item.get("purpose", "") or ""))

    return resolved


@transaction.atomic
def create_execution(*, actor, organisation, data):
    """Cria uma execução `prepared` com snapshots e contexto congelado."""
    product = _resolve_product(data["product"], organisation)
    function = _resolve_function(data["function_profile"], organisation)
    instruction_version = _resolve_instruction_version(function)

    context = _resolve_context_versions(
        items=data["context"],
        organisation=organisation,
        product=product,
        instruction_version=instruction_version,
    )

    execution = AIExecution(
        organisation=organisation,
        product=product,
        function_profile=function,
        requested_by=actor,
        title=data["title"],
        objective=data["objective"],
        request_instructions=data["request_instructions"],
        constraints=data.get("constraints", "") or "",
        expected_output_format=data["expected_output_format"],
        execution_mode=data["execution_mode"],
        function_snapshot=_build_function_snapshot(function),
        product_snapshot=_build_product_snapshot(product),
        instruction_version=instruction_version,
    )
    execution.full_clean()
    execution.save()

    for order, (version, purpose) in enumerate(context, start=1):
        ExecutionContextDocument.objects.create(
            execution=execution,
            document_version=version,
            order=order,
            purpose=purpose[:255],
        )

    return execution
