# Generated by Django 2.1.5 on 2019-04-16 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0013_meeting_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='started',
            field=models.BooleanField(default=False),
        ),
    ]
