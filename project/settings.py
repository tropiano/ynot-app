from pathlib import Path
import environ
import os

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent
# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY", default="change_me")
FIELD_ENCRYPTION_KEY = env("FIELD_ENCRYPTION_KEY", default="change_me")

STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="")
STRIPE_ENDPOINT_SECRET = env("STRIPE_ENDPOINT_SECRET", default="")


DEBUG = env("DEBUG", default=False)

ALLOWED_HOSTS = [
    "xtopics.co",
    "www.xtopics.co",
    "localhost",
    "0.0.0.0",
    "127.0.0.1",
    "twitteroptimizer.applikuapp.com",
]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "usermodel.apps.UsermodelConfig",
    "mainapp.apps.MainappConfig",
    "allauth_ui",
    # 3rd party
    "allauth",  # new
    "allauth.account",  # new
    "allauth.socialaccount",  # new
    # social providers
    "allauth.socialaccount.providers.twitter",  # new
    "widget_tweaks",
    # for encryption of variables (user tokens for example)
    "encrypted_model_fields",
    # for local https
    "sslserver",
    # humanize numbers
    "django.contrib.humanize",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "project.context_processors.export_vars",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    # read os.environ['DATABASE_URL'] and raises
    # ImproperlyConfigured exception if not found
    #
    # The db() method is an alias for db_url().
    # "default": env.db(default="sqlite:///db.sqlite3"),
    "default": env.db("DATABASE_URL")
}

if DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql":
    DATABASES["default"]["ATOMIC_REQUESTS"] = True
    DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)
    CI_COLLATION = "und-x-icu"
elif DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3":
    CI_COLLATION = "NOCASE"
elif DATABASES["default"]["ENGINE"] == "django.db.backends.mysql":
    CI_COLLATION = "utf8mb4_unicode_ci"
else:
    raise NotImplementedError("Unknown database engine")
CACHES = {
    # Read os.environ['CACHE_URL'] and raises
    # ImproperlyConfigured exception if not found.
    #
    # The cache() method is an alias for cache_url().
    "default": env.cache(default="dummycache://"),
}
# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
AUTH_USER_MODEL = "usermodel.User"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"": {"handlers": ["console"], "level": "DEBUG"}},
}
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = env.str("STATIC_URL", default="static/")
STATIC_ROOT = env.str("STATIC_ROOT", default=BASE_DIR / "staticfiles")

MEDIA_ROOT = env("MEDIA_ROOT", default=BASE_DIR / "media")
MEDIA_URL = env("MEDIA_PATH", default="/media/")
MEDIA = env("MEDIA", default=MEDIA_URL)

STATICFILES_DIRS = [
    BASE_DIR / "static",
    ("flowbite", BASE_DIR / "node_modules" / "flowbite" / "dist"),
]

AUTHENTICATION_BACKENDS = (
    # "allauth.account.auth_backends.AuthenticationBackend",
    "django.contrib.auth.backends.ModelBackend",
)

SITE_ID = 1
ACCOUNT_EMAIL_VERIFICATION = "none"
LOGIN_REDIRECT_URL = "redirect"
ACCOUNT_LOGOUT_ON_GET = True
