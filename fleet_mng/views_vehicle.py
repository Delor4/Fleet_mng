from django import forms
from django.conf import settings
from django.contrib.admin.models import ADDITION
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic

from fleet_mng.models import Vehicle

# pokazanie listy pojazdów
# /vehicle/ =>  vehicles.html
from fleet_mng.widgets import BootstrapDatePickerInput


class VehiclesView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'fleet_mng.view_vehicle'
    template_name = 'fleet_mng/vehicles.html'

    def get_queryset(self):
        return Vehicle.objects.all().order_by('deleted')


# pokazanie pojedyńczego pojazdu
# / vehicle/<int:pk> =>  vehicle.html
class VehicleView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'fleet_mng.view_vehicle'
    model = Vehicle
    template_name = 'fleet_mng/vehicle.html'


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = (
            'name',
            'brand', 'model', 'generation',
            'registration_number',
            'checkup', 'insurance',
            'mileage',
            'description')
        labels = {
            'name': 'Nazwa',
            'brand': 'Marka',
            'model': 'Model',
            'generation': 'Typ',
            'registration_number': 'Nr rejestracyjny',
            'description': 'Uwagi',
            'mileage': 'Przebieg',
            'checkup': 'Badanie techniczne',
            'insurance': 'Ubezpieczenie',
        }
        widgets = {
            'checkup': BootstrapDatePickerInput(),
            'insurance': BootstrapDatePickerInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@login_required
@permission_required('fleet_mng.add_vehicle')
def vehicle_new(request):
    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = Vehicle(name=form.cleaned_data.get('name'),
                              brand=form.cleaned_data.get('brand'),
                              model=form.cleaned_data.get('model'),
                              generation=form.cleaned_data.get('generation'),
                              registration_number=form.cleaned_data.get('registration_number'),
                              checkup=form.cleaned_data.get('checkup'),
                              insurance=form.cleaned_data.get('insurance'),
                              mileage=form.cleaned_data.get('mileage'),
                              description=form.cleaned_data.get('description'),
                              )
            vehicle.additional_data['request'] = request
            vehicle.save()
            return HttpResponseRedirect('/vehicle/')
    else:
        form = VehicleForm()

    return render(request, 'fleet_mng/vehicle_new.html', {'form': form})


class VehicleUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'fleet_mng.change_vehicle'
    model = Vehicle
    form_class = VehicleForm
    template_name = 'fleet_mng/vehicle_new.html'
    success_url = '/vehicle/'


@login_required
@permission_required('fleet_mng.delete_vehicle')
def vehicle_delete(request, pk):
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
