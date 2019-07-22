from django.shortcuts import render

from django.http import HttpResponse

from fleetmngapp.models import Vehicle


def index(request):
    return HttpResponse("You're at the app index.")


def vehicles(request):
    return HttpResponse("Vehicles:<br>{}".format('<br>'.join(list(map(lambda x: str(x), Vehicle.objects.all())))))


def vehicle(request, vehicle_id):
    return HttpResponse("Vehicle {}".format(Vehicle.objects.get(id=vehicle_id)))
