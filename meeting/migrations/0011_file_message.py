# Generated by Django 2.1.5 on 2019-04-03 15:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0010_auto_20190402_1859'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='message',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='meeting.Message'),
        ),
    ]