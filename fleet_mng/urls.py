from django.urls import path

from . import views

app_name = 'fleet_mng'
urlpatterns = [
    path('', views.index, name='index'),
    path('vehicles/', views.VehiclesView.as_view(), name='vehicles'),
    path('vehicle/<int:pk>/', views.VehicleView.as_view(), name='vehicle'),
    path('renters/', views.RentersView.as_view(), name='renters'),
    path('renter/<int:pk>/', views.RenterView.as_view(), name='renter'),

    path('rents/', views.RentsView.as_view(), name='rents'),
    path('rent/<int:pk>/', views.RentView.as_view(), name='rent'),
    path('rent/<int:pk>/bring_back/', views.rent_bring_back, name='rent_bring_back'),

    path('week/', views.show_week, name='week'),
    path('week/<int:week_rel>/', views.show_rel_week, name='week_rel'),
    path('week/-<int:week_rel>/', views.show_nrel_week, name='week_nrel'),

    path('rent_form/', views.show_rent_form, name='rent_form'),
]
