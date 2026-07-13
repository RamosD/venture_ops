"""Fundação de empresa e associação utilizador–empresa.

- `Organisation`: empresa (unidade de isolamento). Estado mínimo Activa/Arquivada.
- `Membership`: relação utilizador–empresa com papel mínimo Owner.
- `OrganisationScopedModel`: convenção reutilizável para entidades empresariais
  futuras (relação real e obrigatória com Organisation).

Regras de negócio de onboarding, edição, selector, convites e papéis avançados
NÃO são implementadas aqui (PR10/V1). Aqui apenas a estrutura e a migração.
"""
from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models import UUIDPrimaryKeyModel


class Organisation(UUIDPrimaryKeyModel):
    """Empresa/workspace — contexto obrigatório e unidade de isolamento."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Activa"
        ARCHIVED = "archived", "Arquivada"

    name = models.CharField("nome", max_length=255)
    status = models.CharField(
        "estado", max_length=16, choices=Status.choices, default=Status.ACTIVE
    )

    class Meta:
        db_table = "organisations_organisation"
        verbose_name = "empresa"
        verbose_name_plural = "empresas"

    def __str__(self) -> str:
        return self.name


class Membership(UUIDPrimaryKeyModel):
    """Associação utilizador–empresa–papel. No MVP: única, papel Owner."""

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(
        "papel", max_length=16, choices=Role.choices, default=Role.OWNER
    )
    is_active = models.BooleanField("activa", default=True)

    class Meta:
        db_table = "organisations_membership"
        verbose_name = "associação"
        verbose_name_plural = "associações"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organisation"],
                name="uniq_membership_user_organisation",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} @ {self.organisation} ({self.role})"


class OrganisationScopedModel(UUIDPrimaryKeyModel):
    """Convenção reutilizável para entidades empresariais futuras.

    Toda a entidade empresarial pertence obrigatoriamente a uma `Organisation`
    (relação real, não nula). O `organisation_id` é definido pelo servidor a
    partir do contexto de empresa (PR11) — nunca aceite livremente do cliente.
    `PROTECT` evita a eliminação silenciosa de dados empresariais.
    """

    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_set",
        editable=False,
    )

    class Meta:
        abstract = True
