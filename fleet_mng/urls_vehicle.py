from django.urls import path

from fleet_mng import views_vehicle

urlpatterns = [
    path('', views_vehicle.VehiclesView.as_view(), name='vehicles'),
    path('<int:pk>/', views_vehicle.VehicleView.as_view(), name='vehicle'),
]
