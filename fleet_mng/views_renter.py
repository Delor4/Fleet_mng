from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic

from fleet_mng.models import Renter


# widok dla listy obiektów modelu Rent
class RentersView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'fleet_mng.view_renter'
    template_name = 'fleet_mng/renters.html'

    def get_queryset(self):
        return Renter.objects.all()

# widok dla pojedyńczego obiektu modelu Rent
class RenterView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'fleet_mng.view_renter'
    model = Renter
    template_name = 'fleet_mng/renter.html'
