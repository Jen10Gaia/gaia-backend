import uuid

from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

class Religion(models.TextChoices):
    Christian = 'Christian'
    Muslim = 'Muslim'
    Buddhist = 'Buddhist'
    Atheist = 'Atheist'
    Agnostic = 'Agnostic'
    Other = 'Other'


class Gender(models.TextChoices):
    Male = 'Male'
    Female = 'Female'


class FirstTimeVisaApplication(models.TextChoices):
    Yes = 'Yes'
    No = 'No'


class MedicalCondition(models.TextChoices):
    Yes = 'Yes'
    No = 'No'


class Married(models.TextChoices):
    Yes = 'Yes'
    No = 'No'


# Create your models here.
class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, related_name='userprofile', on_delete=models.CASCADE)
    phoneNumber = models.IntegerField( null=True)
    firstTimeVisaApplication = models.CharField(
        max_length=20,
        choices=FirstTimeVisaApplication.choices,
        default=FirstTimeVisaApplication.Yes,
        null=True
    )
    medicalCondition = models.CharField(
        max_length=20,
        choices=MedicalCondition.choices,
        default=MedicalCondition.Yes,
        null=True
    )
    medicalConditionDescription = models.CharField(max_length=255, blank=True, default='', null=True)
    married = models.CharField(
        max_length=20,
        choices=Married.choices,
        default=Married.Yes,
        null=True
    )
    religion = models.CharField(
        max_length=20,
        choices=Religion.choices,
        default=Religion.Christian,
        null=True
    )
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        default=Gender.Male,
        null=True
    )
    academicPapers = models.FileField(null=True)
    bankStatements = models.FileField(null=True)
    resume = models.FileField(null=True)


@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    user = instance

    if created:
        profile = UserProfile(user=user)
        profile.save()
