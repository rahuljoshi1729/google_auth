# Generated by Django 4.2.7 on 2023-11-03 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_g', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(default=None, max_length=100),
        ),
    ]
