# Generated by Django 4.1.7 on 2023-06-13 16:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0004_rename_accomodation_school_accomodation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='tuitionFee',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(1000000)]),
        ),
    ]
