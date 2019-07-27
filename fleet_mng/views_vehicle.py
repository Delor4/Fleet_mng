from django import forms
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic

from fleet_mng.models import Vehicle


# pokazanie listy pojazdów
# /vehicle/ =>  vehicles.html
class VehiclesView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'fleet_mng.view_vehicle'
    template_name = 'fleet_mng/vehicles.html'

    def get_queryset(self):
        return Vehicle.objects.all()


# pokazanie pojedyńczego pojazdu
# / vehicle/<int:pk> =>  vehicle.html
class VehicleView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'fleet_mng.view_vehicle'
    model = Vehicle
    template_name = 'fleet_mng/vehicle.html'


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ('name', 'brand', 'model', 'generation', 'registration_number')

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
                              )
            vehicle.save()
            return HttpResponseRedirect('/')
    else:
        form = VehicleForm()

    return render(request, 'fleet_mng/vehicle_new.html', {'form': form})


class VehicleUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'fleet_mng.change_vehicle'
    model = Vehicle
    form_class = VehicleForm
    template_name = 'fleet_mng/vehicle_new.html'
    success_url = '/vehicle/'
