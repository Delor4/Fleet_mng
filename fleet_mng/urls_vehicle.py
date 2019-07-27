from django.urls import path

from fleet_mng import views_vehicle

urlpatterns = [
    path('', views_vehicle.VehiclesView.as_view(), name='vehicles'),
    path('<int:pk>/', views_vehicle.VehicleView.as_view(), name='vehicle'),
    path('new/', views_vehicle.vehicle_new, name='vehicle_new'),
    path('<int:pk>/edit/', views_vehicle.VehicleUpdateView.as_view(), name='vehicle_edit'),

]
