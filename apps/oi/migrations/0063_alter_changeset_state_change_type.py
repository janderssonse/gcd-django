from django.db import migrations, models


class Migration(migrations.Migration):
    # Schema-safe: adds choices to existing IntegerFields. `choices` is
    # enforced by Django, not the database, so this emits no DDL
    # (verify with `sqlmigrate oi 0063`).

    dependencies = [
        ('oi', '0062_add_character_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changeset',
            name='change_type',
            field=models.IntegerField(
                choices=[(0, 'Unknown'), (1, 'Publisher'), (2, 'Brand'),
                         (3, 'Indicia Publisher'), (4, 'Series'),
                         (5, 'Issue Add'), (6, 'Issue'), (7, 'Cover'),
                         (8, 'Issue Bulk'), (9, 'Variant Add'),
                         (10, 'Two Issues'), (11, 'Reprint'), (12, 'Image'),
                         (13, 'Brand Group'), (14, 'Brand Use'),
                         (15, 'Series Bond'), (16, 'Creator'),
                         (17, 'Creator Art Influence'), (18, 'Received Award'),
                         (19, 'Creator Degree'), (20, 'Creator Membership'),
                         (21, 'Creator Non Comic Work'), (22, 'Creator Relation'),
                         (23, 'Creator School'), (24, 'Award'), (25, 'Feature'),
                         (26, 'Feature Logo'), (27, 'Feature Relation'),
                         (28, 'Printer'), (29, 'Indicia Printer'),
                         (30, 'Creator Signature'), (31, 'Character'),
                         (32, 'Group'), (33, 'Group Membership'),
                         (34, 'Character Relation'), (35, 'Group Relation'),
                         (36, 'Universe'), (37, 'Story Arc'),
                         (38, 'Story Arc Relation')],
                db_index=True),
        ),
        migrations.AlterField(
            model_name='changeset',
            name='state',
            field=models.IntegerField(
                choices=[(99, 'Available'), (0, 'Baseline'), (1, 'Editing'),
                         (2, 'Pending Review'), (3, 'In Discussion'),
                         (4, 'Under Review'), (5, 'Approved'), (6, 'Discarded')],
                db_index=True),
        ),
    ]
