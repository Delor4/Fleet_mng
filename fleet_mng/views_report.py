import pytz
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django import forms

from fleet_mng.widgets import BootstrapDatePickerInput


class ReportDateForm(forms.Form):
    report_date = forms.DateField(widget=BootstrapDatePickerInput,
                                  label="Wybierz datę:",
                                  initial=timezone.now().date())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# pokazanie widoku raportu dla podanej daty
# /report/<year>-<month>-<day>  =>    report.html
@login_required
@permission_required('fleet_mng.can_show_week')
def show_report_date(request, year, month, day):
    if request.method == "POST":
        form = ReportDateForm(request.POST)
        if form.is_valid():
            report_date = form.cleaned_data.get('report_date')
            return HttpResponseRedirect(
                '/report/{0}-{1}-{2}/'.format(report_date.year, report_date.month, report_date.day)
            )
    else:
        form = ReportDateForm()
        naive = timezone.datetime(int(year), int(month), int(day))
        t = pytz.timezone("Europe/Warsaw").localize(naive, is_dst=None)

    return render(request, 'fleet_mng/report.html', {'form': form,
                                                     'week': 'Tablica',
                                                     'reports': 'Raporty',
                                                     })


# wywołanie podstawowego widoku (bez danych)
@login_required
@permission_required('fleet_mng.can_show_week')
def show_report(request, template='fleet_mng/report.html'):
    if request.method == "POST":
        return show_report_date(request, None, None, None)
    return render(request, template,
                  {'form': ReportDateForm(),
                   'week': None,
                   'reports': None,
                   })
