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

    def __str__(self) -> str:
        return "{0} [{1} {2}]".format(self.name, self.brand, self.model)

    def is_rented(self) -> bool:
        return Rent.objects.filter(vehicle=self, rented__exact=1).exists()

    def is_not_bring_back(self) -> bool:
        rents = Rent.objects.filter(vehicle=self)
        for rent in rents:
            if rent.is_not_bring_back():
                return True
        return False

    def is_free(self):
        return not Rent.objects.filter(vehicle=self, rented__exact=1).exists()


class Renter(models.Model):
    name = models.CharField(max_length=193, db_index=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return "{}".format(self.name)


class Rent(models.Model):
    description = models.TextField(blank=True)
    from_date = models.DateField(default=timezone.now)
    to_date = models.DateField()
    vehicle = models.ForeignKey(Vehicle, on_delete=models.DO_NOTHING)
    renter = models.ForeignKey(Renter, on_delete=models.DO_NOTHING)
    rented = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return "{3}, {4}: {0} - {1}: {2}".format(self.from_date,
                                                 self.to_date,
                                                 self.description,
                                                 self.vehicle,
                                                 self.renter)

    class Meta:
        permissions = (("can_mark_returned", "Set vehicle as returned"),)

    def is_not_bring_back(self) -> bool:
        return self.to_date < timezone.now().date() and self.from_date < timezone.now().date() and self.rented == 1
