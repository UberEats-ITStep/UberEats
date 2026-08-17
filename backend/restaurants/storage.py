"""
Media storage abstraction.

Every image field in this app (Restaurant.image, MenuItem.image) already
delegates file I/O to Django's storage API rather than touching the
filesystem directly, so today they use `default_storage`
(FileSystemStorage) with zero special-casing.

To move to a cloud provider later:

    # settings.py, Django >= 4.2
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",  # django-storages
        },
        "staticfiles": {...},
    }

or for Cloudinary:

    STORAGES = {"default": {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"}}

No changes to models.py, serializers.py, views.py, or the seed command are
required — `FieldFile.url` and `.save()` already go through whatever
backend is configured. `get_media_storage()` exists as a single import
point for any code (e.g. the seed command) that wants to reference the
active storage explicitly rather than going through a model field.
"""
from django.core.files.storage import default_storage


def get_media_storage():
    return default_storage