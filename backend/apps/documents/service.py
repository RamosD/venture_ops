"""Serviço documental: criação, edição, recuperação e coordenação BD↔storage.

Concentra as regras de domínio e a transaccionalidade. O servidor deriva a
empresa do contexto; o cliente nunca envia `organisation`, `storage_key`,
`checksum` nem `version_number`.

Fronteira de fonte de verdade (artefacto 05): a BD guarda apenas metadados; o
**conteúdo Markdown** vive no armazenamento privado (`StorageAdapter`),
referenciado por `DocumentVersion.storage_key`.

Coordenação BD↔armazenamento (SEC-STO-01):
1. o objecto privado é escrito **antes** de criar a referência oficial na BD;
2. enquanto a transacção de BD não confirmar, nada na aplicação expõe o objecto
   (só é alcançável via `DocumentVersion`, cuja linha ainda não está visível);
3. se a escrita falhar, não se cria `DocumentVersion` nem se altera
   `current_version`;
4. se a transacção de BD falhar depois da escrita, tenta-se remover o objecto
   órfão de forma controlada; se a remoção falhar, regista-se `storage.failure`;
5. `current_version` nunca aponta para um objecto inexistente.

Limitação residual (documentada, sem fila nem transacção distribuída): uma falha
abrupta do processo **entre** a escrita do objecto e o commit da BD pode deixar
um objecto órfão no armazenamento (nunca referenciado, portanto inócuo do ponto
de vista de exposição). A reconciliação/garbage-collection de órfãos fica como
tarefa operacional futura (fora do âmbito do MVP).

Concorrência optimista (padrão real de `Product`): cada mutação bloqueia a linha
do `Document` (`select_for_update`), valida `Document.version` contra
`expected_version` e incrementa-a exactamente uma vez; versão obsoleta →
`VersionConflict`.
"""
from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings
from django.db import models, transaction

from apps.audit.models import AuditAction, AuditResult
from apps.audit.service import record_event
from apps.documents.models import Document, DocumentVersion, ExportPolicy
from apps.portfolio.models import Product
from apps.storage import get_storage
from apps.storage.exceptions import ObjectTooLargeError, StorageError

# Marcadores editáveis por metadados (além de title/document_type/product).
MARKER_FIELDS = ("is_outdated", "export_policy")
META_FIELDS = ("title", "document_type") + MARKER_FIELDS


class DocumentServiceError(Exception):
    """Base dos erros de domínio documental."""


class DocumentNotFound(DocumentServiceError):
    """Documento inexistente no contexto da empresa (→ 404)."""


class ProductNotInOrganisation(DocumentServiceError):
    """Produto inexistente ou de outra empresa (→ tratado como 400/404)."""


class VersionConflict(DocumentServiceError):
    """`expected_version` não corresponde à versão actual (→ 409)."""


class DocumentVersionNotFound(DocumentServiceError):
    """Número de versão inexistente no documento (→ 404)."""


class ContentTooLarge(DocumentServiceError):
    """Conteúdo excede o limite configurado (→ 413)."""


class InvalidContentEncoding(DocumentServiceError):
    """Conteúdo não é texto UTF-8 válido (→ 400)."""


@dataclass(frozen=True)
class _PreparedContent:
    """Objecto já escrito no armazenamento (antes de referenciar na BD)."""

    storage_key: str
    checksum: str
    byte_size: int


# --- Utilitários de conteúdo ------------------------------------------------
def encode_content(content: str) -> bytes:
    """Valida UTF-8 e o limite; devolve os bytes a persistir.

    Levanta `InvalidContentEncoding` (UTF-8 inválido, ex.: surrogates isolados)
    ou `ContentTooLarge` (acima de `DOCUMENT_MAX_BYTES`).
    """
    if content is None:
        content = ""
    try:
        data = content.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise InvalidContentEncoding() from exc
    if len(data) > settings.DOCUMENT_MAX_BYTES:
        raise ContentTooLarge()
    return data


def _write_object(data: bytes) -> _PreparedContent:
    """Escreve o objecto privado e devolve a referência (antes da BD)."""
    storage = get_storage()
    try:
        stored = storage.save(data)
    except ObjectTooLargeError as exc:
        raise ContentTooLarge() from exc
    return _PreparedContent(
        storage_key=stored.key, checksum=stored.checksum, byte_size=stored.size
    )


def _discard_object(storage_key: str, *, actor, organisation, document_id) -> None:
    """Remove um objecto órfão de forma controlada; audita falhas de remoção."""
    try:
        get_storage().delete(storage_key)
    except StorageError:
        # A remoção falhou: o objecto fica órfão (não referenciado → inócuo).
        # Regista com o evento aprovado da lista fechada.
        record_event(
            action=AuditAction.STORAGE_FAILURE,
            actor=actor,
            organisation=organisation,
            entity_type="document",
            entity_id=str(document_id) if document_id else "",
            result=AuditResult.FAILURE,
            metadata={"operation": "orphan_cleanup", "stage": "delete"},
        )


def read_content(version: DocumentVersion) -> str:
    """Lê e descodifica o conteúdo de uma versão a partir do armazenamento."""
    data = get_storage().open(version.storage_key)
    return data.decode("utf-8")


def _resolve_product(product_id, organisation) -> Product:
    """Devolve o produto da MESMA empresa ou erro (isolamento — RT-01)."""
    product = Product.objects.filter(pk=product_id, organisation=organisation).first()
    if product is None:
        raise ProductNotInOrganisation()
    return product


def _abbrev_checksum(checksum: str) -> str:
    """Checksum abreviado para metadados de auditoria (nunca o conteúdo)."""
    return checksum[:12]


# --- Criação ----------------------------------------------------------------
def create_document(
    *,
    actor,
    organisation,
    title,
    document_type,
    content: str,
    product_id=None,
    is_outdated=None,
    export_policy=None,
):
    """Cria um documento, a versão 1 e a referência de conteúdo privado.

    Escreve o objecto antes da BD; em falha de BD após a escrita, remove o
    objecto órfão. Audita `document.created` e `document.version_created`.
    """
    data = encode_content(content)  # valida UTF-8 + limite (413/400) antes de escrever

    product = None
    if product_id is not None:
        product = _resolve_product(product_id, organisation)

    prepared = _write_object(data)  # objecto escrito; ainda não referenciado

    try:
        with transaction.atomic():
            document = Document(
                organisation=organisation,
                product=product,
                title=title,
                document_type=document_type,
            )
            if is_outdated is not None:
                document.is_outdated = is_outdated
            if export_policy is not None:
                document.export_policy = export_policy
            document.full_clean()
            document.save()

            version = DocumentVersion(
                document=document,
                version_number=1,
                storage_key=prepared.storage_key,
                checksum=prepared.checksum,
                byte_size=prepared.byte_size,
                author=actor,
            )
            version.save()

            document.current_version = version
            document.save(update_fields=["current_version", "updated_at"])
    except Exception:
        # Transacção revertida: a linha da versão não existe → objecto órfão.
        _discard_object(
            prepared.storage_key,
            actor=actor,
            organisation=organisation,
            document_id=None,
        )
        raise

    _audit_created(actor, organisation, document, version)
    return document, version


# --- Carregamento com bloqueio ----------------------------------------------
def _load_locked(organisation, document_id, expected_version) -> Document:
    """Bloqueia a linha do documento da empresa do contexto e valida a versão."""
    document = (
        Document.objects.select_for_update()
        .filter(pk=document_id, organisation=organisation)
        .first()
    )
    if document is None:
        raise DocumentNotFound()
    if document.version != expected_version:
        raise VersionConflict()
    return document


def _next_version_number(document) -> int:
    """Próximo número sequencial de versão do documento (linha já bloqueada)."""
    current_max = document.versions.aggregate(m=models.Max("version_number"))["m"] or 0
    return current_max + 1


# --- Edição -----------------------------------------------------------------
def update_document(
    *,
    actor,
    organisation,
    document_id,
    expected_version,
    content=None,
    change_summary="",
    meta_changes=None,
):
    """Edição com concorrência optimista.

    Se `content` for fornecido, cria uma nova `DocumentVersion` (a anterior
    permanece imutável) e actualiza `current_version`. Alterações de metadados
    (`meta_changes`) aplicam-se ao documento. Em ambos os casos `version` é
    validada contra `expected_version` e incrementada exactamente uma vez.
    """
    meta_changes = dict(meta_changes or {})

    data = None
    if content is not None:
        data = encode_content(content)  # valida antes de bloquear/escrever

    # Resolve o produto (se enviado) fora da transacção de escrita.
    if "product" in meta_changes and meta_changes["product"] is not None:
        _resolve_product(meta_changes["product"], organisation)

    prepared: _PreparedContent | None = None
    if data is not None:
        prepared = _write_object(data)

    try:
        with transaction.atomic():
            document = _load_locked(organisation, document_id, expected_version)

            changed_fields: list[str] = []
            new_version = None

            # Metadados.
            for field in META_FIELDS:
                if field in meta_changes:
                    setattr(document, field, meta_changes[field])
                    changed_fields.append(field)
            if "product" in meta_changes:
                document.product = (
                    _resolve_product(meta_changes["product"], organisation)
                    if meta_changes["product"] is not None
                    else None
                )
                changed_fields.append("product")

            # Conteúdo → nova versão imutável.
            if prepared is not None:
                new_version = DocumentVersion(
                    document=document,
                    version_number=_next_version_number(document),
                    storage_key=prepared.storage_key,
                    checksum=prepared.checksum,
                    byte_size=prepared.byte_size,
                    author=actor,
                    change_summary=change_summary or "",
                )
                new_version.save()
                document.current_version = new_version
                changed_fields.append("content")

            document.version = document.version + 1
            document.full_clean()
            document.save()
    except Exception:
        if prepared is not None:
            _discard_object(
                prepared.storage_key,
                actor=actor,
                organisation=organisation,
                document_id=document_id,
            )
        raise

    _audit_updated(actor, organisation, document, new_version, changed_fields)
    return document, new_version, changed_fields


# --- Recuperação ------------------------------------------------------------
def restore_version(
    *, actor, organisation, document_id, version_number, expected_version, change_summary=""
):
    """Recupera uma versão antiga criando uma **nova** versão com o seu conteúdo.

    Não altera nem apaga versões anteriores. Preserva o checksum de origem nos
    metadados mínimos e reutiliza o mesmo `storage_key` (conteúdo imutável e
    idêntico — sem reescrita nem objecto órfão). Audita `document.version_restored`.
    """
    with transaction.atomic():
        document = _load_locked(organisation, document_id, expected_version)

        source = document.versions.filter(version_number=version_number).first()
        if source is None:
            raise DocumentVersionNotFound()

        summary = change_summary or f"Recuperado da versão {version_number}"
        new_version = DocumentVersion(
            document=document,
            version_number=_next_version_number(document),
            # Conteúdo idêntico e imutável → reutiliza o objecto existente.
            storage_key=source.storage_key,
            checksum=source.checksum,
            byte_size=source.byte_size,
            author=actor,
            change_summary=summary[:255],
        )
        new_version.save()

        document.current_version = new_version
        document.version = document.version + 1
        document.save(update_fields=["current_version", "version", "updated_at"])

    record_event(
        action=AuditAction.DOCUMENT_VERSION_RESTORED,
        actor=actor,
        organisation=organisation,
        entity_type="document",
        entity_id=str(document.pk),
        result=AuditResult.SUCCESS,
        metadata={
            "operation": "restore",
            "from_version": version_number,
            "to_version": new_version.version_number,
            "document_version": document.version,
            "checksum": _abbrev_checksum(new_version.checksum),
        },
    )
    return document, new_version


# --- Auditoria (eventos 5–7; metadados sem conteúdo integral) ----------------
def _audit_created(actor, organisation, document, version) -> None:
    record_event(
        action=AuditAction.DOCUMENT_CREATED,
        actor=actor,
        organisation=organisation,
        entity_type="document",
        entity_id=str(document.pk),
        result=AuditResult.SUCCESS,
        metadata={
            "operation": "create",
            "document_type": document.document_type,
            "document_version": document.version,
        },
    )
    record_event(
        action=AuditAction.DOCUMENT_VERSION_CREATED,
        actor=actor,
        organisation=organisation,
        entity_type="document",
        entity_id=str(document.pk),
        result=AuditResult.SUCCESS,
        metadata={
            "operation": "create_version",
            "version": version.version_number,
            "checksum": _abbrev_checksum(version.checksum),
        },
    )


def _audit_updated(actor, organisation, document, new_version, changed_fields) -> None:
    record_event(
        action=AuditAction.DOCUMENT_UPDATED,
        actor=actor,
        organisation=organisation,
        entity_type="document",
        entity_id=str(document.pk),
        result=AuditResult.SUCCESS,
        metadata={
            "operation": "update",
            "fields": sorted(changed_fields),
            "document_version": document.version,
        },
    )
    if new_version is not None:
        record_event(
            action=AuditAction.DOCUMENT_VERSION_CREATED,
            actor=actor,
            organisation=organisation,
            entity_type="document",
            entity_id=str(document.pk),
            result=AuditResult.SUCCESS,
            metadata={
                "operation": "create_version",
                "version": new_version.version_number,
                "checksum": _abbrev_checksum(new_version.checksum),
            },
        )
