import datetime

import pytz
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.utils import timezone
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


def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + datetime.timedelta(n)


@login_required
@permission_required('fleet_mng.can_show_week')
def show_week_rel(request, week_rel=0):
    show_from = timezone.now() + datetime.timedelta(int(week_rel) * 7)
    return show_week(request, show_from)


@login_required
@permission_required('fleet_mng.can_show_week')
def show_week_date(request, year, month, day):
    naive = timezone.datetime(int(year), int(month), int(day))
    t = pytz.timezone("Europe/Warsaw").localize(naive, is_dst=None)
    return show_week(request, t)


@login_required
@permission_required('fleet_mng.can_show_week')
def show_week(request, show_from=timezone.now()):
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

    # dates for nav
    prev_date = show_from + datetime.timedelta(-1)
    prev_week_date = show_from + datetime.timedelta(-7)
    next_date = show_from + datetime.timedelta(+1)
    next_week_date = show_from + datetime.timedelta(+7)

    return render(request, 'fleet_mng/week.html',
                  {'rents_list': week, 'show_from': show_from, 'show_to': show_to, 'weeks': weeks, 'days': days,
                   'rents_table': tabl,
                   'nav': {
                       'prev': {
                           'year': prev_date.year,
                           'month': prev_date.month,
                           'day': prev_date.day,
                       },
                       'prev_week': {
                           'year': prev_week_date.year,
                           'month': prev_week_date.month,
                           'day': prev_week_date.day,
                       },
                       'next': {
                           'year': next_date.year,
                           'month': next_date.month,
                           'day': next_date.day,
                       },
                       'next_week': {
                           'year': next_week_date.year,
                           'month': next_week_date.month,
                           'day': next_week_date.day,
                       },
                   },
                   })
