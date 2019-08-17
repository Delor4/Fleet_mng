from django.urls import path, re_path, include

from . import views

app_name = 'fleet_mng'
urlpatterns = [
    path('', views.index, name='index'),

    path('vehicle/', include('fleet_mng.urls_vehicle')),
    path('renter/', include('fleet_mng.urls_renter')),
    path('rent/', include('fleet_mng.urls_rent')),

    path('week/', views.show_week, name='week'),
    re_path(r'^week/(?P<week_rel>-?\d+)/$', views.show_week_rel, name='week_rel'),
    re_path(r'^week/(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/$', views.show_week_date, name='week_date'),
    re_path(r'^week/ajax/(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/$', views.ajax_show_week_date, name='ajax_week_date'),

    path('user/', include('fleet_mng.urls_user')),

    path('report/', include('fleet_mng.urls_report')),
]
