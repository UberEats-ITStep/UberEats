from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_normalize_role_values'),
    ]

    operations = [
        migrations.CreateModel(
            name='VerificationCode',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('code_hash', models.CharField(max_length=128)),
                (
                    'purpose',
                    models.CharField(
                        choices=[('PASSWORD_RESET', 'Password reset')],
                        max_length=32,
                    ),
                ),
                ('expires_at', models.DateTimeField(db_index=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='verification_codes',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'indexes': [
                    models.Index(
                        fields=['user', 'purpose', 'created_at'],
                        name='users_verif_user_id_b033ba_idx',
                    ),
                ],
            },
        ),
    ]