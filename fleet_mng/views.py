from django.shortcuts import render, get_object_or_404
from fleet_mng.models import Vehicle, Renter, Rent


def index(request):
    return render(request, 'fleet_mng/index.html', {'sites_list': ['vehicles', 'renters', 'rents']})


def vehicles(request):
    vehicles_list = Vehicle.objects.all()
    context = {'vehicles_list': vehicles_list}
    return render(request, 'fleet_mng/vehicles.html', context)


def vehicle(request, vehicle_id):
    car = get_object_or_404(Vehicle, pk=vehicle_id)
    return render(request, 'fleet_mng/vehicle.html', {'vehicle': car})


def renters(request):
    renters_list = Renter.objects.all()
    context = {'renters_list': renters_list}
    return render(request, 'fleet_mng/renters.html', context)


def renter(request, renter_id):
    renter = get_object_or_404(Renter, pk=renter_id)
    return render(request, 'fleet_mng/renter.html', {'renter': renter})


def rents(request):
    rents_list = Rent.objects.all()
    context = {'rents_list': rents_list}
    return render(request, 'fleet_mng/rents.html', context)


def rent(request, rent_id):
    rent = get_object_or_404(Rent, pk=rent_id)
    return render(request, 'fleet_mng/rent.html', {'rent': rent})
