from django.urls import path

from . import views

app_name = 'fleet_mng'
urlpatterns = [
    path('', views.index, name='index'),
    path('vehicles/', views.vehicles, name='vehicles'),
    path('vehicle/<int:pk>/', views.VehicleView.as_view(), name='vehicle'),
    path('renters/', views.renters, name='renters'),
    path('renter/<int:pk>/', views.RenterView.as_view(), name='renter'),
    path('rents/', views.rents, name='rents'),
    path('rent/<int:pk>/', views.RentView.as_view(), name='rent'),

    path('week/', views.show_week, name='week')
]
