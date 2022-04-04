# Generated by Django 4.0.2 on 2022-04-03 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0022_post_subcontractorcontact_alter_file_timestamp_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='contact',
            field=models.CharField(default='', max_length=128, verbose_name='Le nom du contact'),
        ),
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1648988486.252038, verbose_name='Timestamp de mise à jour'),
        ),
    ]
