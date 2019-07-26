from django.views import generic

from fleet_mng.models import Renter


class RentersView(generic.ListView):
    template_name = 'fleet_mng/renters.html'

    def get_queryset(self):
        return Renter.objects.all()


class RenterView(generic.DetailView):
    model = Renter
    template_name = 'fleet_mng/renter.html'
