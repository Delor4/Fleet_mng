from django.urls import path

from . import views

urlpatterns = [
    path('', views.RentersView.as_view(), name='renters'),
    path('<int:pk>/', views.RenterView.as_view(), name='renter'),
]
