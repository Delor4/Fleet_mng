from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse, Http404
from django.template import loader

from fleet_mng.models import Vehicle, Renter


def index(request):
    return render(request, 'fleet_mng/index.html', {'sites_list': ['vehicles', 'renters']})


def vehicles(request):
    vehicles_list = Vehicle.objects.all()
    context = {'vehicles_list': vehicles_list}
    return render(request, 'fleet_mng/vehicles.html', context)


def vehicle(request, vehicle_id):
    try:
        car = Vehicle.objects.get(pk=vehicle_id)
    except Vehicle.DoesNotExist:
        raise Http404("Vehicle does not exist")
    return render(request, 'fleet_mng/vehicle.html', {'vehicle': car})


def renters(request):
    renters_list = Renter.objects.all()
    context = {'renters_list': renters_list}
    return render(request, 'fleet_mng/renters.html', context)


def renter(request, renter_id):
    renter = get_object_or_404(Renter, pk=renter_id)
    return render(request, 'fleet_mng/renter.html', {'renter': renter})
