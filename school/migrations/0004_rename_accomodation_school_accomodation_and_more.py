# Generated by Django 4.1.7 on 2023-05-26 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0003_school_accomodation_school_institution_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='school',
            old_name='Accomodation',
            new_name='accomodation',
        ),
        migrations.AlterField(
            model_name='school',
            name='course',
            field=models.CharField(choices=[('Business', 'Business'), ('Information Technology', 'It'), ('Finance', 'Finance'), ('Education', 'Education'), ('Health', 'Health'), ('Telecommunication', 'Telecommunication'), ('Architecture', 'Architecture'), ('Engineering', 'Engineering'), ('Arts', 'Arts'), ('Law', 'Law'), ('Others', 'Others')], default='Business', max_length=30),
        ),
    ]
