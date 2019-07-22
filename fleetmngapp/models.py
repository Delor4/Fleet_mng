from django.db import models
from django.utils import timezone


class Vehicle(models.Model):
    name = models.CharField(max_length=193, db_index=True)

    brand = models.CharField(max_length=193)
    model = models.CharField(max_length=193)
    generation = models.CharField(max_length=193, blank=True)
    registration_number = models.CharField(max_length=193)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return "{0} [{1} {2}]".format(self.name, self.brand, self.model)

    def is_rented(self):
        return Rent.objects.filter(vehicle=self, to_date__gte=timezone.now()).exists() or Rent.objects.filter(
            vehicle=self, from_date__gte=timezone.now()).exists()


class Renter(models.Model):
    name = models.CharField(max_length=193, db_index=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return "{}".format(self.name)


class Rent(models.Model):
    description = models.TextField(blank=True)
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    vehicle = models.ForeignKey(Vehicle, on_delete=models.DO_NOTHING)
    renter = models.ForeignKey(Renter, on_delete=models.DO_NOTHING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return "{3}, {4}: {0} - {1}: {2}".format(self.from_date,
                                                 self.to_date,
                                                 self.description,
                                                 self.vehicle,
                                                 self.renter)
