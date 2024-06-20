from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.home, name='home'),
    path('user-home/', views.user_home, name='user_home'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('play/', views.play, name='play'),
    path('submission-result/<int:attempted_question_pk>/', views.submission_result, name='submission_result'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('guest-login/', views.guest_login, name='guest_login'),
    path('about/', views.about, name='about'),

]
