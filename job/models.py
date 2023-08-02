import uuid
from datetime import *
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

import geocoder
from decimal import Decimal
import os

from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point

from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class JobType(models.TextChoices):
	Permanent = 'Permanent'
	Temporary = 'Temporary'

class Country(models.TextChoices):
	UK = 'UK'
	USA = 'USA'
	Canada = 'Canada'
	Australia = 'Australia'

class Education(models.TextChoices):
	Certificate = 'Certificate'
	Diploma = 'Diploma'
	Bachelors = 'Bachelors'
	Masters = 'Masters'
	Phd = 'Phd'

class Industry(models.TextChoices):
	Business = 'Business'
	IT = 'Information Technology'
	Banking = 'Banking'
	Education = 'Education'
	Telecommunication = 'Telecommunication'
	Transportation = 'Transportation'
	Health = 'Health'
	Engineering = 'Engineering'
	Construction = 'Construction'
	Others = 'Others'

class Experience(models.TextChoices):
	NO_EXPERIENCE = 'No Experience'
	ONE_YEAR = '1 Years'
	TWO_YEAR = '2 Years'
	THREE_YEAR_PLUS = '3 Years above'

class Status(models.TextChoices):
	Pending = 'Pending'
	Approved = 'Approved'
	Rejected = 'Rejected'   


def return_date_time():
	#now = timezone.now()
	now = datetime.now()
	return now + timedelta(days=10)

class Job(models.Model):
	id = models.UUIDField(primary_key = True, default = uuid.uuid4,editable = False, unique=True)
	title = models.CharField(max_length=200, null=True)
	description = models.TextField(null=True)
	email = models.EmailField(null=True)
	address = models.CharField(max_length=100, null=True)
	jobType = models.CharField(
		max_length=20,
		choices=JobType.choices,
		default=JobType.Permanent
	)
	country = models.CharField(
		max_length=20,
		choices=Country.choices,
		default=Country.UK	
	)
	education = models.CharField(
		max_length=20,
		choices=Education.choices,
		default=Education.Bachelors
	)
	industry = models.CharField(
		max_length=30,
		choices=Industry.choices,
		default=Industry.Business
	)
	experience = models.CharField(
		max_length=20,
		choices=Experience.choices,
		default=Experience.NO_EXPERIENCE
	)

	salary = models.IntegerField(default=1, validators=[ MinValueValidator(1), MaxValueValidator(1000000)])
	positions = models.IntegerField(default=1)
	company = models.CharField(max_length=100, null=True)
	# point = gismodels.PointField(default=Point(0.0, 0.0))
	price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
	lastDate = models.DateTimeField(default=return_date_time)
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	createdAt = models.DateTimeField(auto_now_add=True)
	
	def save(self, *args, **kwargs):
		#geocoder(self)
		super(Job, self).save(*args, **kwargs)
	
		
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
	job = models.ForeignKey(Job, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
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

