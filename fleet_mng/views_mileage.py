from django import forms
from django.conf import settings
from django.contrib.admin.models import ADDITION
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic

from fleet_mng.models import Vehicle, MileageChecks

from fleet_mng.widgets import BootstrapDatePickerInput


class MileageAddForm(forms.Form):
    mileage = forms.IntegerField(label="Nowy przegląd:",
                                 initial=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def mileages_shared(request, pk, form):
    vehicle = Vehicle.objects.get(pk=pk)
    mileages = MileageChecks.objects.filter(vehicle=vehicle)
    return render(request, 'fleet_mng/mileages.html', {
        'mileages_list': mileages,
        'vehicle': vehicle,
        'form': form,
    })


@login_required
@permission_required('fleet_mng.add_vehicle')
def mileages(request, pk):
    if request.method == 'POST':
        form = MileageAddForm(request.POST)
        if form.is_valid():
            next_check = form.cleaned_data.get('mileage')
            vehicle = Vehicle.objects.get(pk=pk)
            mileage = MileageChecks(vehicle=vehicle, next_check=next_check)
            mileage.save()
            return HttpResponseRedirect(
                '/mileage/{0}/'.format(pk)
            )
    else:
        form = MileageAddForm()
    return mileages_shared(request, pk, form)


@login_required
@permission_required('fleet_mng.add_vehicle')
def mileage_new(request, pk):
    if request.method == 'POST':
        vehicle = Vehicle.objects.get(pk=pk)

    return mileages(request, pk)


@login_required
@permission_required('fleet_mng.delete_vehicle')
def mileage_confirm(request, vpk, mpk):
    if request.method == 'POST' and \
            int(request.POST['confirm']) == 1:
        vehicle = Vehicle.objects.get(pk=vpk)
        if int(request.POST['delete']) == 1:
            vehicle.deleted = 1
        else:
            vehicle.deleted = 0
        vehicle.additional_data['request'] = request
        vehicle.save()
    return HttpResponseRedirect('/vehicle/')
