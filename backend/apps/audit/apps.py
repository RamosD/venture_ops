from django.apps import AppConfig


class AuditConfig(AppConfig):
    """Registo append-only: actor, entidade, operação e correlação."""

    name = "apps.audit"
    label = "audit"
