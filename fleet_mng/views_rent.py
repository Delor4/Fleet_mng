import datetime
import pytz
from django import forms
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.views import generic

from fleet_mng.models import Vehicle, Renter, Rent
from fleet_mng.widgets import BootstrapDatePickerInput


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
    to_date = forms.DateField(widget=BootstrapDatePickerInput,
                              label="Przewidywana data zwrotu:",
                              initial=timezone.now().date() + datetime.timedelta(+7))
    vehicle = forms.ChoiceField(label="Dostępne pojazdy:")
    renter = forms.ChoiceField(label="Wypożyczający:")

    new_renter = forms.CharField(max_length=191, required=False, label="Nowy wypożyczający, nazwisko:")
    new_renter_description = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(),
        label="Nowy wypożyczający, uwagi:",
        required=False
    )
    description = forms.CharField(
        label='Uwagi:',
        max_length=2000,
        widget=forms.Textarea(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        search_str = kwargs.pop('search_str', None)
        super().__init__(*args, **kwargs)
        v = Vehicle.objects.raw(
            'select * from fleet_mng_vehicle where deleted = 0 and id not in '
            '(select distinct(vehicle_id) from fleet_mng_rent where rented = 1)')
        self.fields['vehicle'].initial = search_str
        self.fields['vehicle'].choices = [(x.id, x) for x in v]

        renters = Renter.objects.exclude(deleted=1)
        self.fields['renter'].choices = [(0, '-- nowy --')]
        self.fields['renter'].choices.extend([(x.id, x) for x in renters])

    def clean(self):
        cleaned_data = super(RentForm, self).clean()

        to_date = cleaned_data.get('to_date')
        if not to_date:
            raise forms.ValidationError('Niewłaściwa data.')
        if to_date < timezone.now().date():
            raise forms.ValidationError('Nie można wybrać przeszłej daty!')  # past date

        vehicle = cleaned_data.get('vehicle')
        if not vehicle:
            raise forms.ValidationError('Wybierz pojazd.')
        if not Vehicle.objects.get(id=int(vehicle)).is_free():
            raise forms.ValidationError('Pojazd niedostępny.')

        renter = cleaned_data.get('renter')

        new_renter = cleaned_data.get('new_renter')
        new_renter_description = cleaned_data.get('new_renter_description')

        if (not renter or int(renter) == 0) and (not new_renter or new_renter == ''):
            raise forms.ValidationError('Wpisz nazwisko nowego użytkownika.')


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
                renter_db = Renter(last_name=new_renter, description=new_renter_description)
                renter_db.save()
            else:
                renter_db = Renter.objects.get(id=renter)

            d = form.cleaned_data.get('to_date')
            naive = timezone.datetime(d.year, d.month, d.day)
            t = pytz.timezone("Europe/Warsaw").localize(naive, is_dst=None)

            description = form.cleaned_data.get('description')
            rent_db = Rent(to_date=t,
                           vehicle=v,
                           renter=renter_db,
                           description=description)
            rent_db.save()

            return HttpResponseRedirect('/week/')
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
    return HttpResponseRedirect('/week/')


class RentUpdateForm(forms.Form):
    to_date = forms.DateField(widget=BootstrapDatePickerInput,
                              label="Przewidywana data zwrotu:",
                              initial=timezone.now().date() + datetime.timedelta(+7))

    vehicle = forms.CharField(label="Pojazd:", disabled=True, required=False)

    renter = forms.ChoiceField(label="Wypożyczający:")

    new_renter = forms.CharField(max_length=191, required=False, label="Nowy wypożyczający, nazwisko:")
    new_renter_description = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(),
        label="Nowy wypożyczający, uwagi:",
        required=False
    )
    description = forms.CharField(
        label='Uwagi:',
        max_length=2000,
        widget=forms.Textarea(),
        required=False
    )
    backed = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    def __init__(self, *args, **kwargs):
        search_str = kwargs.pop('search_str', None)
        super().__init__(*args, **kwargs)

        renters = Renter.objects.exclude(deleted=1)
        self.fields['renter'].choices = [(0, '-- nowy --')]
        self.fields['renter'].choices.extend([(x.id, x) for x in renters])

    def clean(self):
        cleaned_data = super(RentUpdateForm, self).clean()

        to_date = cleaned_data.get('to_date')
        if not to_date:
            raise forms.ValidationError('Niewłaściwa data.')
        if to_date < timezone.now().date():
            raise forms.ValidationError('Nie można wybrać przeszłej daty!')  # past date

        renter = cleaned_data.get('renter')

        new_renter = cleaned_data.get('new_renter')
        new_renter_description = cleaned_data.get('new_renter_description')

        if (not renter or int(renter) == 0) and (not new_renter or new_renter == ''):
            raise forms.ValidationError('Wpisz nazwisko nowego użytkownika!')


class RentUpdateBackedForm(forms.Form):
    to_date = forms.CharField(label="Data zwrotu:",
                              disabled=True, required=False)
    vehicle = forms.CharField(label="Pojazd:", disabled=True, required=False)
    renter = forms.CharField(label="Wypożyczający:", disabled=True, required=False)

    description = forms.CharField(
        label='Uwagi:',
        max_length=2000,
        widget=forms.Textarea(),
        required=False
    )
    backed = forms.IntegerField(widget=forms.HiddenInput(), initial=1)

    def __init__(self, *args, **kwargs):
        search_str = kwargs.pop('search_str', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(RentUpdateBackedForm, self).clean()


# /rent/<int>/edit/    =>  rent_new.html
@login_required
@permission_required('fleet_mng.change_rent')
def show_rent_update_form(request, pk):
    form = None
    if request.method == 'POST':
        if request.POST['backed'] != '1':
            form = RentUpdateForm(request.POST)
        else:
            form = RentUpdateBackedForm(request.POST)
        if form.is_valid():
            if request.POST['backed'] != '1':
                renter = int(form.cleaned_data.get('renter'))
                new_renter = form.cleaned_data.get('new_renter')
                new_renter_description = form.cleaned_data.get('new_renter_description')

                renter_db = None
                if renter == 0:
                    renter_db = Renter(last_name=new_renter, description=new_renter_description)
                    renter_db.save()
                else:
                    renter_db = Renter.objects.get(id=renter)

                d = form.cleaned_data.get('to_date')
                naive = timezone.datetime(d.year, d.month, d.day)
                t = pytz.timezone("Europe/Warsaw").localize(naive, is_dst=None)

            rent_db = Rent.objects.get(id=pk)
            if request.POST['backed'] != '1':
                rent_db.to_date = t
                rent_db.renter = renter_db
            rent_db.description = form.cleaned_data.get('description')
            rent_db.save()
            return HttpResponseRedirect('/week/')
    else:
        rent = Rent.objects.get(id=pk)
        if not rent.rented:
            form = RentUpdateBackedForm(
                initial={'description': rent.description, 'vehicle': rent.vehicle.name, 'to_date': rent.to_date,
                         'renter': rent.renter})
        else:
            form = RentUpdateForm(
                initial={'to_date': rent.to_date, 'renter': rent.renter.id, 'description': rent.description,
                         'vehicle': rent.vehicle.name})

    return render(request, 'fleet_mng/rent_new.html', {'form': form})
