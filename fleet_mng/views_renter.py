from django import forms
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from django.views.generic import UpdateView

from fleet_mng.models import Renter


# widok dla listy obiektów modelu Renter
# /renter/
class RentersView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'fleet_mng.view_renter'
    template_name = 'fleet_mng/renters.html'

    def get_queryset(self):
        return Renter.objects.all()


# widok dla pojedyńczego obiektu modelu Renter
# /renter/<int:pk>
class RenterView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'fleet_mng.view_renter'
    model = Renter
    template_name = 'fleet_mng/renter.html'


class RenterForm(forms.ModelForm):
    class Meta:
        model = Renter
        fields = ('last_name', 'first_name', 'description')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@login_required
@permission_required('fleet_mng.add_renter')
def renter_new(request):
    if request.method == "POST":
        form = RenterForm(request.POST)
        if form.is_valid():
            renter = Renter(last_name=form.cleaned_data.get('last_name'),
                            first_name=form.cleaned_data.get('first_name'),
                            description=form.cleaned_data.get('description'),
                            )
            renter.save()
            return HttpResponseRedirect('/renter/')
    else:
        form = RenterForm()

    return render(request, 'fleet_mng/renter_new.html', {'form': form})


class RenterUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'fleet_mng.change_renter'
    model = Renter
    form_class = RenterForm
    template_name = 'fleet_mng/renter_new.html'
    success_url = '/renter/'
