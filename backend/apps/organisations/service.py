"""Serviço de onboarding e gestão mínima da empresa.

Usa as entidades `Organisation` e `Membership` já criadas em PR02 (não as
recria). O papel Owner é atribuído pelo serviço; o cliente nunca escolhe o papel
nem o `organisation_id` operacional (derivado sempre da Membership no servidor).
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from apps.organisations.models import Membership, Organisation


class OnboardingError(Exception):
    """Erro genérico de onboarding/empresa."""


class AlreadyHasOrganisationError(OnboardingError):
    """O utilizador já tem empresa (segunda empresa bloqueada no MVP)."""


class NoOrganisationError(OnboardingError):
    """O utilizador não tem empresa activa."""


class NotOwnerError(OnboardingError):
    """A operação exige o papel Owner."""


def get_active_membership(user) -> Membership | None:
    return (
        Membership.objects.select_related("organisation")
        .filter(user=user, is_active=True)
        .first()
    )


@transaction.atomic
def complete_onboarding(user, name: str) -> Organisation:
    """Cria Organisation activa + Membership Owner de forma transaccional.

    Serializa por utilizador com `select_for_update` para que pedidos
    concorrentes não criem duas empresas.
    """
    # Bloqueio da linha do utilizador: concorrentes esperam e vêem a Membership
    # criada pelo primeiro, sendo então bloqueados.
    locked_user = get_user_model().objects.select_for_update().get(pk=user.pk)

    if Membership.objects.filter(user=locked_user).exists():
        raise AlreadyHasOrganisationError()

    organisation = Organisation.objects.create(
        name=name.strip(), status=Organisation.Status.ACTIVE
    )
    try:
        # Savepoint: a constraint de "uma Membership activa por utilizador" é a
        # garantia final de BD contra corridas; se disparar, revertemos tudo
        # (sem Organisation órfã).
        with transaction.atomic():
            Membership.objects.create(
                user=locked_user,
                organisation=organisation,
                role=Membership.Role.OWNER,  # atribuído pelo serviço, não pelo cliente
                is_active=True,
            )
    except IntegrityError as exc:
        raise AlreadyHasOrganisationError() from exc
    return organisation


def edit_organisation(user, name: str) -> Organisation:
    """Edita o nome da empresa do próprio utilizador (só Owner)."""
    membership = get_active_membership(user)
    if membership is None:
        raise NoOrganisationError()
    if membership.role != Membership.Role.OWNER:
        raise NotOwnerError()
    organisation = membership.organisation
    organisation.name = name.strip()
    organisation.save(update_fields=["name", "updated_at"])
    return organisation
