

STATIC_ROOT = "%(django_static_dir)s"
STATIC_URL = "%(django_static_url)s"
MEDIA_ROOT = "%(django_media_dir)s"
MEDIA_URL = "%(django_media_url)s"

DATABASES = {
    "default": {
        # Add "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
        "ENGINE": "django.db.backends.%(db_type)s",
        # DB name or path to database file if using sqlite3.
        "NAME": "%(proj_name)s",
        # Not used with sqlite3.
        "USER": "%(proj_name)s",
        # Not used with sqlite3.
        "PASSWORD": "%(db_pass)s",
        # Set to empty string for localhost. Not used with sqlite3.
        "HOST": "%(database_host)s",
        # Set to empty string for default. Not used with sqlite3.
        "PORT": "%(database_port)s",
    }
}


