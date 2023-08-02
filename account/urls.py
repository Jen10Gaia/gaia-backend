from django.urls import path
from . import views

urlpatterns = [
  path('register/', views.register, name='register'),
  path('me/', views.currentUser, name='current_user'),
  path('me/update/', views.updateUser, name='update_user'),
  path('update/profile/', views.updateUserProfile, name='update_profile'),
  path('upload/resume/', views.uploadResume, name='upload_resume'),
  path('upload/bank-statements/', views.uploadBankStatements, name='upload_bank_statements'),
  path('upload/academic-documents/', views.uploadAcademicPapers, name='upload_academic_documents'),
  path('admin/check/', views.isAdminCheck, name='admin-check'),
  path('admin/dashboard/users/', views.getAllUsers, name='get-all-users'),
]