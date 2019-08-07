import datetime

import pytz
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from fleet_mng.models import Rent, Vehicle


# strona główna
# /     => index.html
def index(request):
    return render(request, 'fleet_mng/index.html')


# pokazanie widoku od danego tygodnia (relatywnie w stosunku do aktualnego)
# /week/3   - pokazanie od dnia za 3 tygodnie
# /week/-2  - pokazanie od dnia sprzed 2 tygodni

# /week/<number:week_rel>   =>  week.html
@login_required
@permission_required('fleet_mng.can_show_week')
def show_week_rel(request, week_rel=0):
    show_from = timezone.now() + datetime.timedelta(int(week_rel) * 7)
    return show_week(request, show_from)


# pokazanie widoku od podanej daty
# /week/<year>-<month>-<day>  =>    week.html
@login_required
@permission_required('fleet_mng.can_show_week')
def show_week_date(request, year, month, day):
    naive = timezone.datetime(int(year), int(month), int(day))
    t = pytz.timezone("Europe/Warsaw").localize(naive, is_dst=None)
    return show_week(request, t)


def make_links_for_nav(nav):
    nav['link'] = reverse('fleet_mng:week_date',
                          args=(nav['year'], nav['month'], nav['day'])
                          )
    nav['ajax_link'] = reverse('fleet_mng:ajax_week_date',
                               args=(nav['year'], nav['month'], nav['day'])
                               )


@login_required
@permission_required('fleet_mng.can_show_week')
def ajax_show_week_date(request, year, month, day):
    naive = timezone.datetime(int(year), int(month), int(day))
    t = pytz.timezone("Europe/Warsaw").localize(naive, is_dst=None)
    nav = get_nav_from_date(t)
    make_links_for_nav(nav['prev'])
    make_links_for_nav(nav['prev_week'])
    make_links_for_nav(nav['next'])
    make_links_for_nav(nav['next_week'])
    nav['today_link'] = reverse('fleet_mng:week_date', args=(year, month, day))
    nav['today_ajax_link'] = reverse('fleet_mng:ajax_week_date', args=(year, month, day))
    return JsonResponse(
        {
            'table_html': show_week(request, t, 'fleet_mng/_week_table.html').content.decode('utf-8'),
            'nav': nav
        }
    )


# funkcja podaje wszystkie dni pomiędzy datami (włącznie z końcami)
def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + datetime.timedelta(n)


days_names = ['Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'So', 'Nd']


def get_nav_from_date(s_date):
    prev_date = s_date + datetime.timedelta(-1)
    prev_week_date = s_date + datetime.timedelta(-7)
    next_date = s_date + datetime.timedelta(+1)
    next_week_date = s_date + datetime.timedelta(+7)
    return {
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
        }
    }


# właściwe wywołanie widoku
@login_required
@permission_required('fleet_mng.can_show_week')
def show_week(request, show_from=timezone.now(), template='fleet_mng/week.html'):
    show_to = show_from + datetime.timedelta((4 * 7) - 1)
    from_range = show_from
    to_range = show_to
    rents = Rent.objects.filter(from_date__lte=to_range).filter(to_date__gte=from_range)

    # fill days
    days = [datetime.date(d.year, d.month, d.day) for d in date_range(from_range, to_range)]
    week_days = [days_names[d.weekday()] for d in days]

    vehicles_data = {}
    vehicles = Vehicle.objects.exclude(deleted=1)
    # initialize vehicles table
    for vehicle in vehicles:
        vehicles_data[vehicle] = [{'present': 0, 'rents': [], 'classes': []} for _ in range(len(days))]

    '''
    f_  -   first
    m_  -   middle
    l_  -   last
    b_  -   not bring back
    r_  -   rented
    n_  -   has note
    '''

    # filling table
    for rent in rents:
        if rent.vehicle.deleted:
            continue
        last = int((rent.to_date - rent.from_date).days)
        for i, d in enumerate(date_range(rent.from_date, rent.to_date)):
            if d in days:
                tab_item = vehicles_data[rent.vehicle][days.index(d)]
                tab_item['present'] = 1
                tab_item['rents'].append(rent)
                tab_item['classes'].append('m_' + str(rent.id))
                if rent.rented:
                    tab_item['classes'].append('r_' + str(rent.id))
                if rent.is_not_bring_back():
                    tab_item['classes'].append('b_' + str(rent.id))
                if i == 0:
                    tab_item['classes'].append('f_' + str(rent.id))
                    if rent.description:
                        tab_item['classes'].append('n_' + str(rent.id))
                if i == last:
                    tab_item['classes'].append('l_' + str(rent.id))

    return render(request, template,
                  {'days': days,
                   'week_days': week_days,
                   'rents_list': rents,
                   'vehicles_table': vehicles_data,
                   'dates': {
                       'from': show_from,
                       'to': show_to,
                   },
                   'nav': get_nav_from_date(show_from),
                   'dock': settings.DOCK
                   })
