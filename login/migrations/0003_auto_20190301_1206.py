# Generated by Django 2.1.5 on 2019-03-01 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_auto_20190301_1201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_id',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='user id'),
        ),
    ]
