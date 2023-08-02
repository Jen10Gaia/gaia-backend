from rest_framework import status
from rest_framework.response import Response

def can_user_modify_service(service, request):
  if service.user != request.user:
    return Response({'message': 'You can not update this job'}, status=status.HTTP_403_FORBIDDEN)
  else:
    return None
