from django.urls import path

from . import views_renter

urlpatterns = [
    path('', views_renter.RentersView.as_view(), name='renters'),
    path('<int:pk>/', views_renter.RenterView.as_view(), name='renter'),
    path('new/', views_renter.renter_new, name='renter_new'),
    path('<int:pk>/edit/', views_renter.RenterUpdateView.as_view(), name='renter_edit'),
]
