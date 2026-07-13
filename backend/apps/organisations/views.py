"""Endpoints de onboarding e empresa (contexto derivado da Membership)."""
from __future__ import annotations

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import AuditAction, AuditResult
from apps.audit.service import record_event
from apps.organisations import service
from apps.organisations.context import deny_cross_org, require_context


def _org_payload(org) -> dict:
    return {"id": str(org.pk), "name": org.name, "status": org.status}


class OnboardingView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_protect)
    def post(self, request: Request) -> Response:
        name = (request.data.get("name") or "").strip()
        if not name:
            return Response(
                {"detail": "O nome da empresa é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            organisation = service.complete_onboarding(request.user, name)
        except service.AlreadyHasOrganisationError:
            return Response(
                {"detail": "Já existe uma empresa associada a esta conta."},
                status=status.HTTP_409_CONFLICT,
            )
        record_event(
            action=AuditAction.ORGANISATION_CREATED,
            actor=request.user,
            organisation=organisation,
            entity_type="organisation",
            entity_id=str(organisation.pk),
            result=AuditResult.SUCCESS,
        )
        return Response(_org_payload(organisation), status=status.HTTP_201_CREATED)


class OrganisationView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        membership = service.get_active_membership(request.user)
        if membership is None:
            return Response({"organisation": None, "onboarding_required": True})
        return Response(
            {
                "organisation": _org_payload(membership.organisation),
                "onboarding_required": False,
            }
        )

    @method_decorator(csrf_protect)
    def patch(self, request: Request) -> Response:
        name = (request.data.get("name") or "").strip()
        if not name:
            return Response(
                {"detail": "O nome da empresa é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            organisation = service.edit_organisation(request.user, name)
        except service.NoOrganisationError:
            # Sem contexto de empresa (sem Membership activa) → 403.
            return Response(
                {"detail": "Sem empresa associada à conta."},
                status=status.HTTP_403_FORBIDDEN,
            )
        except service.NotOwnerError:
            return Response(
                {"detail": "Apenas o Owner pode editar a empresa."},
                status=status.HTTP_403_FORBIDDEN,
            )
        record_event(
            action=AuditAction.ORGANISATION_UPDATED,
            actor=request.user,
            organisation=organisation,
            entity_type="organisation",
            entity_id=str(organisation.pk),
            result=AuditResult.SUCCESS,
        )
        return Response(_org_payload(organisation))


class OrganisationDetailView(APIView):
    """Acesso por identificador validado contra o contexto de empresa.

    Semente de MVP-18: o cliente não troca de empresa por parâmetro — qualquer id
    diferente do contexto é tratado como acesso cruzado (404 auditado).
    """

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, pk) -> Response:
        _membership, organisation = require_context(request)  # 403 se não houver
        if str(pk) != str(organisation.pk):
            deny_cross_org(request, organisation, pk, "organisation")  # 404 + auditoria
        return Response(_org_payload(organisation))
