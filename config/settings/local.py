from .base import *

DEBUG = True

# Использование файлового хранилища для разработки
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
PRIVATE_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Настройки для разработки
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'