import datetime

import pytz
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django import forms

from fleet_mng.models import Rent
from fleet_mng.views import compute_week_data
from fleet_mng.widgets import BootstrapDatePickerInput


class ReportDateForm(forms.Form):
    report_date = forms.DateField(widget=BootstrapDatePickerInput,
                                  label="Wybierz datę:",
                                  initial=timezone.now().date())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def get_reports(date):
    return Rent.objects.filter(from_date__lte=date).filter(to_date__gte=date)


# pokazanie widoku raportu dla podanej daty
# /report/<year>-<month>-<day>  =>    report.html
@login_required
@permission_required('fleet_mng.change_rent')
def show_report_date(request, year, month, day):
    if request.method == "POST":
        form = ReportDateForm(request.POST)
        if form.is_valid():
            report_date = form.cleaned_data.get('report_date')
            return HttpResponseRedirect(
                '/report/{0}-{1}-{2}/'.format(report_date.year, report_date.month, report_date.day)
            )

    naive = timezone.datetime(int(year), int(month), int(day))
    report_date = pytz.timezone("Europe/Warsaw").localize(naive, is_dst=None)
    from_range = report_date + datetime.timedelta(-7)
    to_range = from_range + datetime.timedelta((4 * 7) - 1)

    form = ReportDateForm(initial={'report_date': report_date})

    week_data = compute_week_data(from_range, to_range, True)

    return render(request, 'fleet_mng/report.html', {'form': form,
                                                     'week': 'Tablica',
                                                     'days': week_data['days'],
                                                     'week_days': week_data['week_days'],
                                                     'rents_list': week_data['rents'],
                                                     'vehicles_table': week_data['vehicles_data'],
                                                     'reports': get_reports(report_date),
                                                     })


# wywołanie podstawowego widoku (bez danych)
@login_required
@permission_required('fleet_mng.change_rent')
def show_report(request, template='fleet_mng/report.html'):
    if request.method == "POST":
        return show_report_date(request, None, None, None)
    return render(request, template,
                  {'form': ReportDateForm(),
                   'week': None,
                   'reports': None,
                   })
