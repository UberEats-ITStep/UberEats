from django.db import migrations


ROLE_MAP = {
    "Client": "CLIENT",
    "Courier": "COURIER",
    "Admin": "ADMIN",
}


def normalize_roles(apps, schema_editor):
    User = apps.get_model("users", "User")
    for old_role, new_role in ROLE_MAP.items():
        User.objects.filter(role=old_role).update(role=new_role)


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_user_role"),
    ]

    operations = [
        migrations.RunPython(normalize_roles, migrations.RunPython.noop),
    ]
