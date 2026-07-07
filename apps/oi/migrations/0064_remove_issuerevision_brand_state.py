from django.db import migrations


class Migration(migrations.Migration):
    # State-only removal of the deprecated `brand` FK on IssueRevision (see
    # gcd 0069). Reconciles model and migration state so
    # `makemigrations --check` is green; the column drop is deferred to the
    # Phase D schema batch, so this emits no DDL.

    dependencies = [
        ('oi', '0063_alter_changeset_state_change_type'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(model_name='issuerevision',
                                       name='brand'),
            ],
            database_operations=[],
        ),
    ]
