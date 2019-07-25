import datetime

import pytz
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views import generic

from fleet_mng.models import Vehicle, Renter, Rent


def index(request):
    sites = ['vehicles', 'renters', 'rents', 'week']
    sites_list = ['fleet_mng:' + x for x in sites]
    return render(request, 'fleet_mng/index.html', {'sites_list': sites_list})


class VehiclesView(generic.ListView):
    template_name = 'fleet_mng/vehicles.html'

    def get_queryset(self):
        return Vehicle.objects.all()


class VehicleView(generic.DetailView):
    model = Vehicle
    template_name = 'fleet_mng/vehicle.html'


class RentersView(generic.ListView):
    template_name = 'fleet_mng/renters.html'

    def get_queryset(self):
        return Renter.objects.all()


class RenterView(generic.DetailView):
    model = Renter
    template_name = 'fleet_mng/renter.html'


class RentsView(generic.ListView):
    template_name = 'fleet_mng/rents.html'

    def get_queryset(self):
        return Rent.objects.all()


class RentView(generic.DetailView):
    model = Rent
    template_name = 'fleet_mng/rent.html'


def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + datetime.timedelta(n)


def show_rel_week(request, week_rel):
    return show_week(request, week_rel)


def show_nrel_week(request, week_rel):
    return show_week(request, -week_rel)


def show_week(request, week_rel=0):
    show_from = timezone.now() + datetime.timedelta(week_rel * 7)
    show_to = show_from + datetime.timedelta((4 * 7) - 1)
    from_range = show_from
    to_range = show_to
    week = Rent.objects.filter(from_date__lte=to_range).filter(to_date__gte=from_range)

    weeks = []
    days = []
    # fill weeks and days
    for i, day in enumerate(date_range(from_range, to_range)):
        days.append(datetime.date(day.year, day.month, day.day))
        if not (i % 7):
            weeks.append(datetime.date(day.year, day.month, day.day))
    tabl = {}

    vehicles = Vehicle.objects.all()
    # initialize vehicles table
    for v in vehicles:
        tabl[v] = [{'present': 0, 'rent': None} for _ in range(len(days))]

    # filling table
    for v in week:
        print("*", v)
        tab_item = {'last': False}
        for i, d in enumerate(date_range(v.from_date, v.to_date)):
            print(i, d)
            da = datetime.date(d.year, d.month, d.day)
            if da in days:
                tab_item = {'present': 1, 'rent': v, 'first': i == 0, 'last': False}
                tabl[v.vehicle][days.index(datetime.date(d.year, d.month, d.day))] = tab_item
            else:
                tab_item = {'last': False}
        tab_item['last'] = True

    return render(request, 'fleet_mng/week.html',
                  {'rents_list': week, 'show_from': show_from, 'show_to': show_to, 'weeks': weeks, 'days': days,
                   'rents_table': tabl,
                   'prev_past': (week_rel - 1) < 0, 'prev_week': abs(week_rel - 1),
                   'next_past': (week_rel + 1) < 0, 'next_week': abs(week_rel + 1),
                   })


class RentForm(forms.Form):
    to_date = forms.DateField()
    vehicle = forms.ChoiceField()
    renter = forms.ChoiceField()

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

    return render(request, 'fleet_mng/rent_form.html', {'form': form})


def rent_bring_back(request, pk):
    if request.method == 'POST' and int(request.POST['confirm']) == 1:
        rent = Rent.objects.get(pk=pk)
        rent.rented = 0
        rent.to_date = timezone.now().date()
        rent.save()
    return HttpResponseRedirect('/')
