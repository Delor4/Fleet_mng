from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('vehicles/', views.vehicles, name='vehicles'),
    path('vehicle/<int:vehicle_id>/', views.vehicle, name='vehicle'),
    path('renters/', views.renters, name='renters'),
    path('renter/<int:renter_id>/', views.renter, name='renter'),
    path('rents/', views.rents, name='rents'),
    path('rent/<int:rent_id>/', views.rent, name='rent'),

    path('week/', views.show_week, name='week')
]
