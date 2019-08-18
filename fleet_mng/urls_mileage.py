from django.urls import path

from fleet_mng import views_mileage

urlpatterns = [
    path('<int:pk>/', views_mileage.mileages, name='mileages'),
    path('<int:pk>/new/', views_mileage.mileage_new, name='mileage_new'),
#    path('<int:vpk>/<int:mpk>/edit/', views_mileage.mileage_edit, name='mileage_edit'),
#    path('<int:vpk>/<int:mpk>/confirm/', views_mileage.mileage_confirm, name='mileage_confirm'),
]
