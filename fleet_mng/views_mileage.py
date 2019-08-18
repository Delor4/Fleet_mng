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


@login_required
@permission_required('fleet_mng.add_vehicle')
def mileages(request, pk):
    vehicle = Vehicle.objects.get(pk=pk)
    mileags = MileageChecks.objects.filter(vehicle=vehicle)
    return render(request, 'fleet_mng/mileages.html', {
        'mileages_list': mileags,
        'vehicle': vehicle,
    })


@login_required
@permission_required('fleet_mng.add_vehicle')
def mileage_new(request, pk):
    return render(request, 'fleet_mng/mileage.html', { })


@login_required
@permission_required('fleet_mng.delete_vehicle')
def mileage_confirm(request, pk):
    if request.method == 'POST' and \
            int(request.POST['confirm']) == 1:
        vehicle = Vehicle.objects.get(pk=pk)
        if int(request.POST['delete']) == 1:
            vehicle.deleted = 1
        else:
            vehicle.deleted = 0
        vehicle.additional_data['request'] = request
        vehicle.save()
    return HttpResponseRedirect('/vehicle/')
