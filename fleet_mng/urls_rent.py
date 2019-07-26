from django.urls import path

from . import views_rent

urlpatterns = [
    path('', views_rent.RentsView.as_view(), name='rents'),
    path('<int:pk>/', views_rent.RentView.as_view(), name='rent'),
    path('new/', views_rent.show_rent_form, name='rent_form'),
    path('bring_back/<int:pk>/', views_rent.rent_bring_back, name='rent_bring_back'),
]
