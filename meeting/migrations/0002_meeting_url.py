# Generated by Django 2.1.5 on 2019-03-13 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='url',
            field=models.CharField(default='DEFAULT', max_length=128),
        ),
    ]