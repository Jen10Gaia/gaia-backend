
from django.urls import path
from . import views

urlpatterns = [
  path('schools/', views.getAllSchools, name='schools'),
  path('schools/new/', views.newSchool, name='new_school'),
  path('schools/<str:pk>/', views.getSchool, name='school'),
  path('schools/<str:pk>/update/', views.updateSchool, name='update_school'),
  path('schools/<str:pk>/delete/', views.deleteSchool, name='delete_school'),
  path('schools/<str:pk>/apply/', views.applyToSchool, name='apply_to_school'),
  path('schools/<str:pk>/check/', views.isApplied, name='is_applied_to_school'),
  path('schools/<str:pk>/candidates/', views.getCandidatesApplied, name='get_candidates_applied'), 
  path('stats/<str:topic>/', views.getTopicStats, name='get_topic_stats'),
  path('me/schools/', views.getCurrentUserSchools, name='current_user_schools'),
  path('me/schools/applied/', views.getCurrentUserAppliedSchools, name='current_user_applied_schools'),
  path('schools/candidates/<str:pk>/approve/', views.approveApplication, name='approve_candidate'),
  path('schools/candidates/<str:pk>/isApproved/', views.isApproved, name='candidate_is_approved'),
  path('schools/candidates/<str:pk>/isRejected/', views.isRejected, name='candidate_is_rejected'),
  path('schools/candidates/<str:pk>/paid/', views.markCandidateAsPaid, name='candidate_has_paid'),

  path('schools/admin/dashboard/orders/', views.orders, name='orders'),
  path('schools/admin/dashboard/revenue/', views.revenue, name='revenue'),

  # path('stripe-webhook-view/<str:pk>/', views.stripe_webhook_view, name='webhook'),

]
