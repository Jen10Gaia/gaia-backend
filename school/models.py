from datetime import *
from django.db import models
from django.contrib.auth.models import User

import geocoder
import uuid
import os

from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point

from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class ScholarshipType(models.TextChoices):
	Full = 'Full-tuition'
	Partial = 'Partial-tuition'
	

class Accomodation(models.TextChoices):
	Yes = 'Yes'
	No = 'No'
	
	
class EducationLevel(models.TextChoices):
	Certificate = 'Certificate'
	Diploma = 'Diploma'
	Bachelors = 'Bachelors'
	Masters = 'Masters'
	Phd = 'Phd'


class Country(models.TextChoices):
	UK = 'UK'
	USA = 'USA'
	Canada = 'Canada'
	Australia = 'Australia'


class Course(models.TextChoices):
	Business = 'Business'
	IT = 'Information Technology'
	Finance = 'Finance'
	Education = 'Education'
	Health = 'Health'
	Telecommunication = 'Telecommunication'
	Architecture = 'Architecture'
	Engineering = 'Engineering'
	Arts = 'Arts'
	Law = 'Law'
	Others = 'Others'

class Status(models.TextChoices):
	Pending = 'Pending'
	Approved = 'Approved'
	Rejected = 'Rejected'   


def return_date_time():
	now = datetime.now()
	return now + timedelta(days=10)


class School(models.Model):
	id = models.UUIDField(primary_key = True, default = uuid.uuid4,editable = False, unique=True)
	title = models.CharField(max_length=200, null=True)
	description = models.TextField(null=True)
	email = models.EmailField(null=True)
	address = models.CharField(max_length=100, null=True)
	scholarshipType = models.CharField(
		max_length=20,
		choices=ScholarshipType.choices,
		default=ScholarshipType.Full
	)
	accomodation = models.CharField(
		max_length=20,
		choices=Accomodation.choices,
		default=Accomodation.Yes
	)
	educationLevel = models.CharField(
		max_length=20,
		choices=EducationLevel.choices,
		default=EducationLevel.Bachelors
	)
	country = models.CharField(
		max_length=20,
		choices=Country.choices,
		default=Country.UK
	)
	course = models.CharField(
		max_length=30,
		choices=Course.choices,
		default=Course.Business
	)

	tuitionFee = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(1000000)], null=True)
	positions = models.IntegerField(default=1)
	institution = models.CharField(max_length=100, null=True)
	# point = gismodels.PointField(default=Point(0.0, 0.0))
	price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
	lastDate = models.DateTimeField(default=return_date_time)
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	createdAt = models.DateTimeField(auto_now_add=True)
	

	def save(self, *args, **kwargs):
		#geocoder(self)
		super(School, self).save(*args, **kwargs)

	def formatted_price(self):
		return "{:,.2f}".format(self.price)

	def geoCoder(self):
		g = geocoder.mapquest(self.address, key=os.environ.get('GEOCODER_API'))

		print(g)

		lng = g.lng
		lat = g.lat

		self.point = Point(lng, lat)


class CandidatesApplied(models.Model):
	id = models.UUIDField(primary_key = True, default = uuid.uuid4,editable = False, unique=True)
	school = models.ForeignKey(School, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='school_candidate_application')
	resume = models.CharField(max_length=200)
	academicPapers = models.CharField(max_length=200)
	bankStatements = models.CharField(max_length=200)
	approved = models.BooleanField(default=False)
	rejected = models.BooleanField(default=False)
	status = models.CharField(
		max_length=20,
		choices=Status.choices,
		default=Status.Pending
	)
	paid = models.BooleanField(default=False)
	appliedAt = models.DateTimeField(auto_now_add=True)
