from django.contrib import admin
from .models import School, CandidatesApplied

class SchoolAdmin(admin.ModelAdmin):
	# Register your models here.
	admin.site.register(School)
	admin.site.register(CandidatesApplied)



