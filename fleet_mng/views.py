import datetime

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views import generic

from fleet_mng.models import Vehicle, Renter, Rent


def index(request):
    sites = ['vehicles', 'renters', 'rents', 'week']
    sites_list = ['fleet_mng:' + x for x in sites]
    return render(request, 'fleet_mng/index.html', {'sites_list': sites_list})


def vehicles(request):
    vehicles_list = Vehicle.objects.all()
    context = {'vehicles_list': vehicles_list}
    return render(request, 'fleet_mng/vehicles.html', context)


class VehicleView(generic.DetailView):
    model = Vehicle
    template_name = 'fleet_mng/vehicle.html'


def renters(request):
    renters_list = Renter.objects.all()
    context = {'renters_list': renters_list}
    return render(request, 'fleet_mng/renters.html', context)


class RenterView(generic.DetailView):
    model = Renter
    template_name = 'fleet_mng/renter.html'


def rents(request):
    rents_list = Rent.objects.all()
    context = {'rents_list': rents_list}
    return render(request, 'fleet_mng/rents.html', context)


class RentView(generic.DetailView):
    model = Rent
    template_name = 'fleet_mng/rent.html'


def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


def show_week(request):
    show_from = timezone.now()
    show_to = show_from + datetime.timedelta(4 * 7)
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
        for i, d in enumerate(date_range(v.from_date, v.to_date)):
            da = datetime.date(d.year, d.month, d.day)
            if da in days:
                tabl[v.vehicle][days.index(datetime.date(d.year, d.month, d.day))] = {'present': 1, 'rent': v}

    return render(request, 'fleet_mng/week.html',
                  {'rents_list': week, 'show_from': show_from, 'show_to': show_to, 'weeks': weeks, 'days': days,
                   'rents_table': tabl})
