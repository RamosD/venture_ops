from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Utilizadores, autenticação, perfil e sessões.

    Nota (F1-P02-PR01): módulo criado vazio. O modelo CustomUser NÃO é criado
    nesta etapa e AUTH_USER_MODEL NÃO é activado. PR02 cria CustomUser, activa
    AUTH_USER_MODEL e gera a primeira migração de forma atómica.
    """

    name = "apps.accounts"
    label = "accounts"
