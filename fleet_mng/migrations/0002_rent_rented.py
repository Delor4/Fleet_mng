# Generated by Django 2.2.3 on 2019-07-23 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet_mng', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rent',
            name='rented',
            field=models.IntegerField(default=1),
        ),
    ]
