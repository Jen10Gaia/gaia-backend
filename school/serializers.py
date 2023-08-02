from rest_framework import serializers
from .models import School, CandidatesApplied

#Necessary to convert data to json
class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields ='__all__'

class CandidatesAppliedSerializer(serializers.ModelSerializer):
  school = SchoolSerializer()
  user_email = serializers.SerializerMethodField()

  class Meta:
    model = CandidatesApplied
    fields = ('id', 'user', 'user_email', 'resume', 'academicPapers', 'bankStatements', 'status', 'approved','paid', 'appliedAt', 'school')

  def get_user_email(self, obj):
    return obj.user.email
  
