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
#/ vehicle/<int:pk> =>  vehicle.html
class VehicleView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'fleet_mng.view_vehicle'
    model = Vehicle
    template_name = 'fleet_mng/vehicle.html'
