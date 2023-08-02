from rest_framework import serializers
from .models import Job, CandidatesApplied

#Necessary to convert data to json
class JobSerializer(serializers.ModelSerializer):
  class Meta:
    model = Job
    fields ='__all__'

class CandidatesAppliedSerializer(serializers.ModelSerializer):
  job = JobSerializer()
  user_email = serializers.SerializerMethodField()

  class Meta:
    model = CandidatesApplied
    fields = ('id','user','user_email', 'resume', 'academicPapers', 'bankStatements', 'approved', 'rejected', 'status',  'paid', 'appliedAt', 'job')

  def get_user_email(self, obj):
    return obj.user.email
  