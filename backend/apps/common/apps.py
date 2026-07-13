from django.apps import AppConfig


class CommonConfig(AppConfig):
    """Utilitários genuinamente partilhados e endpoints técnicos de sistema.

    Limitado a utilitários transversais. Não contém modelos de domínio nem
    abstracções especulativas (sem BaseService/BaseRepository/command bus/etc.).
    """

    name = "apps.common"
    label = "common"
