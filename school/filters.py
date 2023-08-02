from dataclasses import field
from django_filters import rest_framework as filters
from .models import School


class SchoolsFilter(filters.FilterSet):
  #Search
  keyword = filters.CharFilter(field_name='title, course', lookup_expr='icontains')
  location = filters.CharFilter(field_name='address', lookup_expr='icontains')

  #Filters
  min_salary = filters.NumberFilter(field_name="salary" or 0, lookup_expr='gte')
  max_salary = filters.NumberFilter(field_name="salary" or 1000000, lookup_expr='lte')

  class Meta:
    model = School
    fields = ('keyword', 'location','scholarshipType','accomodation', 'educationLevel', 'country', 'course', )