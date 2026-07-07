from django.db import migrations


class Migration(migrations.Migration):
    # The `brand` FK was replaced by the `brand_emblem` m2m and dropped from
    # the models, but no migration reconciled the state, leaving
    # `makemigrations --check` red. Remove it from migration state only; the
    # (nullable, unused) column drop is deferred to the Phase D schema batch,
    # so this emits no DDL.

    dependencies = [
        ('gcd', '0068_alter_issue_is_indexed'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(model_name='issue', name='brand'),
            ],
            database_operations=[],
        ),
    ]
