from django.db import migrations, models


class Migration(migrations.Migration):
    # Schema-safe: adds choices to an existing IntegerField. `choices` is
    # enforced by Django, not the database, so this emits no DDL
    # (verify with `sqlmigrate gcd 0068`).

    dependencies = [
        ('gcd', '0067_add_character_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='is_indexed',
            field=models.IntegerField(
                choices=[(0, 'Skeleton'), (1, 'Some Data'), (2, 'Partial'),
                         (3, 'Ten Percent'), (10, 'Full')],
                db_index=True, default=0),
        ),
    ]
