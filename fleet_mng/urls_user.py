from django.urls import path

from . import views_user

urlpatterns = [
    path('', views_user.show_users, name='users'),
    path('<int:pk>/', views_user.show_user, name='user'),
    path('new/', views_user.new_user, name='user_new'),
]
