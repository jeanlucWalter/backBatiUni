# Generated by Django 4.0.2 on 2022-03-18 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0009_detailedpost_refused_alter_file_timestamp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supervision',
            name='Mission',
        ),
        migrations.AddField(
            model_name='supervision',
            name='superVisionId',
            field=models.IntegerField(default=None, null=True, verbose_name="id de la supervision dans le cas d'une réponse"),
        ),
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1647600135.631121, verbose_name='Timestamp de mise à jour'),
        ),
    ]
