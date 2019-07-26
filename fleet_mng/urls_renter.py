from django.urls import path

from . import views_renter

urlpatterns = [
    path('', views_renter.RentersView.as_view(), name='renters'),
    path('<int:pk>/', views_renter.RenterView.as_view(), name='renter'),
]
