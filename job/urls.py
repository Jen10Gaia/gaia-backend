from django.urls import path
from . import views

urlpatterns = [
  path('jobs/', views.getAllJobs, name='jobs'),
  path('jobs/new/', views.newJob, name='new_job'),
  path('jobs/<str:pk>/', views.getJob, name='job'),
  path('jobs/<str:pk>/update/', views.updateJob, name='update_job'),
  path('jobs/<str:pk>/delete/', views.deleteJob, name='delete_job'),
  path('jobs/<str:pk>/apply/', views.applyToJob, name='apply_to_job'),
  path('jobs/<str:pk>/check/', views.isApplied, name='is_applied_to_job'),
  path('jobs/<str:pk>/candidates/', views.getCandidatesApplied, name='get_candidates_applied'),           
  path('jobs/<str:pk>/checkPositionsLeft/', views.checkPositionsLeft, name='check_positions_left'),           
  path('stats/<str:topic>/', views.getTopicStats, name='get_topic_stats'),
  path('me/jobs/', views.getCurrentUserJobs, name='current_user_jobs'),
  path('me/jobs/applied/', views.getCurrentUserAppliedJobs, name='current_user_applied_jobs'),
  path('candidates/<str:pk>/approve/', views.approveApplication, name='approve_candidate'),
  path('candidates/<str:pk>/isApproved/', views.isApproved, name='candidate_is_approved'),
  path('candidates/<str:pk>/isRejected/', views.isRejected, name='candidate_is_rejected'),
  path('candidates/<str:pk>/paid/', views.markCandidateAsPaid, name='candidate_has_paid'),
  path('admin/dashboard/orders/', views.orders, name='orders'),
  path('admin/dashboard/revenue/', views.revenue, name='revenue'),
  
  # path('candidates/jobs/<str:pk>/paid/check', views.checkCandidateHasPaid, name='check_candidate_has_paid'),
  # path('stripe-webhook-view/<str:pk>/', views.stripe_webhook_view, name='webhook'),
  
    
]