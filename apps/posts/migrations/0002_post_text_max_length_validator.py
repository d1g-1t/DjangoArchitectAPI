# Generated migration — adds MaxLengthValidator to Post.text.
#
# Security context
# ----------------
# Part of the fix for "Django vulnerable to Uncontrolled Resource Consumption"
# (CVE-2024-38875, CVE-2024-41989, CVE-2024-41990, CVE-2024-41991,
#  CVE-2024-45230).
#
# The MaxLengthValidator enforces a hard character limit (50 000) at the
# Django form/serialiser layer.  It does NOT alter the database schema
# (TextField has no length limit in PostgreSQL / SQLite), so this migration
# is state-only — it records the new validator in the migration graph without
# issuing any DDL.

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(
                verbose_name='Текст',
                help_text='Основное содержание поста',
                validators=[
                    django.core.validators.MaxLengthValidator(
                        50000,
                        message='Текст публикации не может превышать 50,000 символов.',
                    )
                ],
            ),
        ),
    ]
