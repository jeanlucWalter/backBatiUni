# Generated by Django 4.0 on 2022-02-08 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0039_rename_company_post_company_remove_candidate_company_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='company',
            new_name='Company',
        ),
        migrations.AlterField(
            model_name='files',
            name='timestamp',
            field=models.FloatField(default=1644313125.589504, verbose_name='Timestamp de mise à jour'),
        ),
    ]
