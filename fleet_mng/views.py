from django.shortcuts import render

from django.http import HttpResponse, Http404
from django.template import loader

from fleet_mng.models import Vehicle


def index(request):
    return HttpResponse("You're at the app index.")


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
