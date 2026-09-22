"""Access the active Django media storage backend.

``settings.STORAGES["default"]`` selects Cloudinary when all Cloudinary
credentials are configured and uses local filesystem storage only in debug
development. Model fields and upload code should continue to use Django's
storage API through their ``FieldFile`` values.
"""
from django.core.files.storage import default_storage


def get_media_storage():
    return default_storage