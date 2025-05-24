from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('main/', views.main_menu, name='main_menu'),
    path('start_quiz/', views.start_quiz, name='start_quiz'),
    path('quiz_question/', views.quiz_question, name='quiz_question'),
    path('check_answer/', views.check_answer, name='check_answer'),
    path('quiz_results/', views.quiz_results, name='quiz_results'),
    path('high_scores/', views.high_scores, name='high_scores'),
]
