from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('user_details/', views.user_details, name='user_details'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add-candidate/', views.add_candidate, name='add_candidate'),
    path('reset-candidates/', views.reset_candidates, name='reset_candidates'),
    path('set-voting-dates/', views.set_voting_dates, name='set_voting_dates'),
    path('update-voting-dates/', views.update_voting_dates, name='update_voting_dates'),
    path('setdate-success/', views.setdate_success, name='setdate_success'),
    path('vote/', views.vote, name='vote'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('voting-not-allowed/', views.voting_not_allowed, name='voting_not_allowed'),


]