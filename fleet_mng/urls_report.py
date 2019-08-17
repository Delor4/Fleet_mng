from django.urls import path, re_path
from . import views_report

urlpatterns = [
    path('', views_report.show_report, name='report'),
    re_path(r'^(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/$',
            views_report.show_report_date,
            name='report_date'),
]
