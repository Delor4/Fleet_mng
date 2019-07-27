import pytz
from django import forms
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.views import generic

from fleet_mng.models import Vehicle, Renter, Rent


# /rent/    =>  rents.html
class RentsView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'fleet_mng.view_rent'
    template_name = 'fleet_mng/rents.html'

    def get_queryset(self):
        return Rent.objects.all()


# /rent/<int:pk>    =>  rent.html
class RentView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'fleet_mng.view_rent'
    model = Rent
    template_name = 'fleet_mng/rent.html'


class RentForm(forms.Form):
    to_date = forms.DateField(label="Przewidywana data zwrotu:")
    vehicle = forms.ChoiceField(label="Dostępne pojazdy:")
    renter = forms.ChoiceField(label="Wypożyczający:")

    new_renter = forms.CharField(max_length=191, required=False)
    new_renter_description = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        search_str = kwargs.pop('search_str', None)
        super().__init__(*args, **kwargs)
        v = Vehicle.objects.raw(
            'select * from fleet_mng_vehicle where id not in '
            '(select distinct(vehicle_id) from fleet_mng_rent where rented = 1)')
        self.fields['vehicle'].initial = search_str
        self.fields['vehicle'].choices = [(x.id, x) for x in v]

        self.fields['renter'].choices = [(0, '-- nowy --')]
        self.fields['renter'].choices.extend([(x.id, x) for x in Renter.objects.all()])

    def clean(self):
        cleaned_data = super(RentForm, self).clean()

        to_date = cleaned_data.get('to_date')
        if to_date < timezone.now().date():
            raise forms.ValidationError('Date can\'t be in past!')

        vehicle = cleaned_data.get('vehicle')
        if not Vehicle.objects.get(id=int(vehicle)).is_free():
            raise forms.ValidationError('Occupied vehicle.')

        renter = cleaned_data.get('renter')

        new_renter = cleaned_data.get('new_renter')
        new_renter_description = cleaned_data.get('new_renter_description')

        if (not renter or int(renter) == 0) and (not new_renter or new_renter == ''):
            raise forms.ValidationError('You have to fill new renter\'s name!')


# /rent/new/    =>  rent_new.html
@login_required
@permission_required('fleet_mng.add_rent')
def show_rent_form(request):
    if request.method == 'POST':
        form = RentForm(request.POST)
        if form.is_valid():
            renter = int(form.cleaned_data.get('renter'))
            new_renter = form.cleaned_data.get('new_renter')
            new_renter_description = form.cleaned_data.get('new_renter_description')

            v = Vehicle.objects.get(id=int(form.cleaned_data.get('vehicle')))

            renter_db = None
            if renter == 0:
                renter_db = Renter(name=new_renter, description=new_renter_description)
                renter_db.save()
            else:
                renter_db = Renter.objects.get(id=renter)

            d = form.cleaned_data.get('to_date')
            naive = timezone.datetime(d.year, d.month, d.day)
            t = pytz.timezone("Europe/Warsaw").localize(naive, is_dst=None)

            rent_db = Rent(to_date=t,
                           vehicle=v,
                           renter=renter_db)
            rent_db.save()

            return HttpResponseRedirect('/')
    else:
        form = RentForm()

    return render(request, 'fleet_mng/rent_new.html', {'form': form})


# /rent/bring_back/<int:pk>/    =>  -
@login_required
@permission_required('fleet_mng.can_mark_returned')
def rent_bring_back(request, pk):
    if request.method == 'POST' and \
            int(request.POST['confirm']) == 1:
        rent = Rent.objects.get(pk=pk)
        rent.rented = 0
        rent.to_date = timezone.now().date()
        rent.save()
    return HttpResponseRedirect('/')
