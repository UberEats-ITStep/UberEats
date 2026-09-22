from django.db import migrations


def migrate_legacy_profile_addresses(apps, schema_editor):
    Profile = apps.get_model('users', 'Profile')
    DeliveryAddress = apps.get_model('users', 'DeliveryAddress')

    profiles = Profile.objects.exclude(address__isnull=True).exclude(address__exact='')
    for profile in profiles.iterator():
        formatted_address = profile.address.strip()
        if not formatted_address:
            continue

        latitude = getattr(profile, 'latitude', None)
        longitude = getattr(profile, 'longitude', None)
        if (latitude is None) != (longitude is None):
            latitude = None
            longitude = None

        DeliveryAddress.objects.update_or_create(
            user_id=profile.user_id,
            label='Home',
            defaults={
                'formatted_address': formatted_address,
                'latitude': latitude,
                'longitude': longitude,
                'is_default': True,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0007_profile_avatar_deliveryaddress'),
        ('users', '0007_profile_latitude_profile_longitude'),
    ]

    operations = [
        migrations.RunPython(
            migrate_legacy_profile_addresses,
            migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name='profile',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='longitude',
        ),
    ]
