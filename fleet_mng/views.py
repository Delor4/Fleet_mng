from django.shortcuts import render

from django.http import HttpResponse
from django.template import loader

from fleet_mng.models import Vehicle


def index(request):
    return HttpResponse("You're at the app index.")


def vehicles(request):
    vehicles_list = Vehicle.objects.all()
    template = loader.get_template('fleet_mng/vehicles.html')
    context = {
        'vehicles_list': vehicles_list,
    }
    return HttpResponse(template.render(context, request))


def vehicle(request, vehicle_id):
    return HttpResponse("Vehicle {}".format(Vehicle.objects.get(id=vehicle_id)))
