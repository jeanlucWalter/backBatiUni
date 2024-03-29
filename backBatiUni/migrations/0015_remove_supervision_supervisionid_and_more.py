# Generated by Django 4.0.2 on 2022-03-21 07:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backBatiUni', '0014_alter_file_timestamp_alter_supervision_supervisionid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supervision',
            name='superVisionId',
        ),
        migrations.AddField(
            model_name='supervision',
            name='Supervision',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='associatedSupervision', to='backBatiUni.supervision', verbose_name='Supervision associée'),
        ),
        migrations.AlterField(
            model_name='file',
            name='timestamp',
            field=models.FloatField(default=1647849217.175152, verbose_name='Timestamp de mise à jour'),
        ),
    ]
