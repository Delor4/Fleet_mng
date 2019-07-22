from django.db import models


class Vehicle(models.Model):
    name = models.CharField(max_length=193, db_index=True)

    brand = models.CharField(max_length=193)
    model = models.CharField(max_length=193)
    generation = models.CharField(max_length=193, blank=True)
    registration_number = models.CharField(max_length=193)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)


class Renter(models.Model):
    name = models.CharField(max_length=193, db_index=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)


class Rent(models.Model):
    description = models.TextField(blank=True)
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    vehicle = models.ForeignKey(Vehicle, on_delete=models.DO_NOTHING)
    renter = models.ForeignKey(Renter, on_delete=models.DO_NOTHING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
