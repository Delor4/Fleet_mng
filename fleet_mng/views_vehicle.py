from django.views import generic

from fleet_mng.models import Vehicle


class VehiclesView(generic.ListView):
    template_name = 'fleet_mng/vehicles.html'

    def get_queryset(self):
        return Vehicle.objects.all()


class VehicleView(generic.DetailView):
    model = Vehicle
    template_name = 'fleet_mng/vehicle.html'
