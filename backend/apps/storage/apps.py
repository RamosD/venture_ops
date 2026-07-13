from django.apps import AppConfig


class StorageConfig(AppConfig):
    """Adaptador de armazenamento documental (contrato mínimo; filesystem/S3 futuros)."""

    name = "apps.storage"
    label = "storage"
