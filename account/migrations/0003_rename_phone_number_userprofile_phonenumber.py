# Generated by Django 4.1.7 on 2023-06-13 17:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_userprofile_phone_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='phone_number',
            new_name='phoneNumber',
        ),
    ]
