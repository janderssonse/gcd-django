# Example settings_local.py for local development.
#
# Copy to settings_local.py (gitignored) and adjust. Anything here
# overrides settings.py. If you use the gcd-django-docker compose setup,
# you do not need this file: its settings_local.py is mounted into the
# web container automatically.

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

# For the gcd-django-docker database reached from the host, use
# HOST 127.0.0.1, PORT 3308, NAME my-gcd-db, USER gcd-django,
# PASSWORD db-gcd. For a locally installed MySQL, adjust as needed.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'my-gcd-db',
        'USER': 'gcd-django',
        'PASSWORD': 'db-gcd',
        'HOST': '127.0.0.1',
        'PORT': '3308',
        'ATOMIC_REQUESTS': True,
    },
}

# No memcached needed outside the containers.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

SILENCED_SYSTEM_CHECKS = ['models.E025',
                          'django_recaptcha.recaptcha_test_key_error']
