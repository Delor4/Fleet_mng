# Generated by Django 2.2.3 on 2019-08-03 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet_mng', '0004_vehicle_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='chekup',
            field=models.DateField(blank=True, null=True, default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vehicle',
            name='mileage',
            field=models.IntegerField(blank=True, default=0),
            preserve_default=False,
        ),
    ]