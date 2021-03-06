from django import forms
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from fleet_mng.models import Vehicle, MileageChecks


class MileageAddForm(forms.Form):
    mileage = forms.IntegerField(label="Nowy przegląd:",
                                 initial=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


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

    vehicle = Vehicle.objects.get(pk=pk)
    mileages = MileageChecks.objects.filter(vehicle=vehicle).order_by('next_check')
    return render(request, 'fleet_mng/mileages.html', {
        'mileages_list': mileages,
        'vehicle': vehicle,
        'form': form,
    })


@login_required
@permission_required('fleet_mng.delete_vehicle')
def mileage_confirm(request, vpk, mpk):
    if request.method == 'POST' and \
            int(request.POST['confirm']) == 1:
        mileage = MileageChecks.objects.get(pk=mpk)
        vehicle = Vehicle.objects.get(pk=vpk)
        if int(request.POST['delete']) == 1:
            mileage.checked = 1
            mileage.checked_mileage = vehicle.mileage
        else:
            mileage.checked = 0
        mileage.additional_data['request'] = request
        mileage.save()
    return HttpResponseRedirect('/mileage/{0}/'.format(vpk))
