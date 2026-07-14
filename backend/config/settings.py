"""Configuração do projecto Django do VentureOps AI (esqueleto — F1-P02-PR01).

Âmbito desta etapa: arranque mínimo do backend modular + DRF + endpoint técnico
/api/system/ping. Sem base de dados, sem autenticação, sem modelos de domínio.
PR02 introduz PostgreSQL, CustomUser (via AUTH_USER_MODEL) e a primeira migração.
"""
from __future__ import annotations

from pathlib import Path

from config.env import get_bool, get_env, get_list

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Segurança / núcleo -----------------------------------------------------
# Chave obrigatória: em falta, o arranque falha com mensagem clara (env.py).
SECRET_KEY = get_env("DJANGO_SECRET_KEY")
DEBUG = get_bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = get_list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# --- Aplicações -------------------------------------------------------------
# contenttypes + auth suportam o modelo de utilizador próprio (PermissionsMixin).
# admin/sessions são introduzidos pelos prompts de autenticação (PR07+).
DJANGO_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
]

# Módulos de domínio do monólito modular (ver docs/produto/00_decisoes_arranque.md).
LOCAL_APPS = [
    "apps.accounts",
    "apps.organisations",
    "apps.portfolio",
    "apps.documents",
    "apps.decisions",
    "apps.work_items",
    "apps.functions",
    "apps.executions",
    "apps.audit",
    "apps.storage",
    "apps.common",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Modelo de utilizador próprio, activo desde a primeira migração (PR02).
AUTH_USER_MODEL = "accounts.CustomUser"

# Validadores de força de palavra-passe (Django).
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Middleware -------------------------------------------------------------
# CorsMiddleware deve preceder CommonMiddleware. Sessão, CSRF e autenticação
# activados em PR07.
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# --- Base de dados (PostgreSQL por configuração de ambiente) ----------------
# Sem SQLite como persistência da aplicação. Configuração obrigatória validada
# no arranque (env.py). O endpoint /api/system/ping não depende da BD.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": get_env("POSTGRES_DB"),
        "USER": get_env("POSTGRES_USER"),
        "PASSWORD": get_env("POSTGRES_PASSWORD"),
        "HOST": get_env("POSTGRES_HOST", default="127.0.0.1"),
        "PORT": get_env("POSTGRES_PORT", default="5432"),
        "CONN_MAX_AGE": int(get_env("POSTGRES_CONN_MAX_AGE", default="0")),
    }
}

# --- Internacionalização ----------------------------------------------------
LANGUAGE_CODE = "pt-pt"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Django REST Framework --------------------------------------------------
# Autenticação por sessão (cookie) e, por defeito, autorização exigida no backend.
# Endpoints públicos (ping/health/auth) declaram AllowAny explicitamente.
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# --- Sessão, cookies e CSRF (SEC-AUTH-01) -----------------------------------
# `Secure` condicional a TLS (explícito por ambiente; falso em desenvolvimento).
_SECURE_COOKIES = get_bool("DJANGO_SECURE_COOKIES", default=False)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = _SECURE_COOKIES
# O frontend lê o token CSRF do cookie e reenvia-o no cabeçalho X-CSRFToken.
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = _SECURE_COOKIES
CSRF_TRUSTED_ORIGINS = get_list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

# --- CORS (restritivo por defeito) ------------------------------------------
# Nenhuma origem é permitida enquanto DJANGO_CORS_ALLOWED_ORIGINS estiver vazia.
# A estratégia local preferida é mesma origem / proxy de desenvolvimento (PR03).
CORS_ALLOWED_ORIGINS = get_list("DJANGO_CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

# --- Armazenamento (adaptador filesystem privado; SEC-DOC-03/04) ------------
# Raiz privada, fora de directórios públicos/servidos. Chaves geradas no
# servidor; sem rota que sirva objectos directamente. S3 não é implementado.
STORAGE_ROOT = get_env("STORAGE_ROOT", default=str(BASE_DIR / "var" / "storage"))
STORAGE_MAX_BYTES = int(get_env("STORAGE_MAX_BYTES", default=str(25 * 1024 * 1024)))
# Limite de bytes do conteúdo documental (UTF-8). Excedido → 413. Por defeito
# alinhado com o limite do armazenamento; configurável por ambiente e nos testes.
DOCUMENT_MAX_BYTES = int(get_env("DOCUMENT_MAX_BYTES", default=str(STORAGE_MAX_BYTES)))
# Limite de bytes do pacote de contexto gerado (Markdown único ou ZIP). Excedido
# → 413, antes de devolver qualquer conteúdo (nunca pacote parcial). Configurável
# por ambiente e nos testes.
CONTEXT_PACKAGE_MAX_BYTES = int(
    get_env("CONTEXT_PACKAGE_MAX_BYTES", default=str(STORAGE_MAX_BYTES))
)

# --- Correio (consola em dev; configurável para SMTP real no piloto) --------
EMAIL_BACKEND = get_env(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = get_env("DJANGO_EMAIL_HOST", default="")
EMAIL_PORT = int(get_env("DJANGO_EMAIL_PORT", default="25"))
EMAIL_HOST_USER = get_env("DJANGO_EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = get_env("DJANGO_EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = get_bool("DJANGO_EMAIL_USE_TLS", default=False)
DEFAULT_FROM_EMAIL = get_env(
    "DJANGO_DEFAULT_FROM_EMAIL", default="no-reply@ventureops.local"
)

# --- Recuperação de acesso e rate limiting (SEC-AUTH-01/02) -----------------
# Rate limiting persistente em PostgreSQL (controlo de segurança, não throttling
# de conveniência): funciona com vários processos, sem Redis.
PASSWORD_RESET_TTL_SECONDS = int(get_env("PASSWORD_RESET_TTL_SECONDS", default="1800"))
RATE_LIMIT_LOGIN_MAX = int(get_env("RATE_LIMIT_LOGIN_MAX", default="5"))
RATE_LIMIT_LOGIN_WINDOW = int(get_env("RATE_LIMIT_LOGIN_WINDOW", default="300"))
RATE_LIMIT_RECOVERY_MAX = int(get_env("RATE_LIMIT_RECOVERY_MAX", default="5"))
RATE_LIMIT_RECOVERY_WINDOW = int(get_env("RATE_LIMIT_RECOVERY_WINDOW", default="900"))
# Retenção dos registos de rate limiting (limpeza operacional). Tem de ser
# superior à maior janela activa (900s); default 24h para preservar histórico
# recente sem deixar a tabela crescer indefinidamente.
RATE_LIMIT_RETENTION_SECONDS = int(
    get_env("RATE_LIMIT_RETENTION_SECONDS", default="86400")
)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Aceleração da suite de testes ------------------------------------------
# Hasher rápido **apenas** quando a suite de testes corre (`manage.py test`).
# Não altera o comportamento de segurança em runtime real (produção usa os
# hashers por omissão do Django). Evita que o PBKDF2 domine o tempo dos testes
# de API (muitas autenticações por teste).
import sys as _sys  # noqa: E402

if "test" in _sys.argv:
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
