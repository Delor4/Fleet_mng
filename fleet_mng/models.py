from django.db import models
from django.utils import timezone


# dane pojazdu
class Vehicle(models.Model):
    # nazwa pojazdu
    name = models.CharField(max_length=193, db_index=True)

    # marka, model, wersja
    brand = models.CharField(max_length=193)
    model = models.CharField(max_length=193)
    generation = models.CharField(max_length=193, blank=True)
    # nr rej.
    registration_number = models.CharField(max_length=193)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    # ciąg znaków opisujący obiekt
    def __str__(self) -> str:
        return "{0} [{1} {2}]".format(self.name, self.brand, self.model)

    # zwraca True gdy pojazd jest wynajęty
    def is_rented(self) -> bool:
        return Rent.objects.filter(vehicle=self, rented__exact=1).exists()

    # zwraca True gdy pojazd jest wynajęty i minął czas wynajęcia
    def is_not_bring_back(self) -> bool:
        rents = Rent.objects.filter(vehicle=self)
        for rent in rents:
            if rent.is_not_bring_back():
                return True
        return False

    # zwraca True gdy pojazd nie jest wynajęty
    def is_free(self):
        return not self.is_rented()

    # zwraca aktualnych wypożyczających ten pojazd
    def get_current_renters(self):
        return Rent.objects.filter(vehicle=self, rented__exact=1)


# Wypożyczający
class Renter(models.Model):
    # krótka nazwa
    last_name = models.CharField(max_length=193)
    first_name = models.CharField(max_length=193, blank=True)
    # dłuższy opis
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        tmp = self.first_name
        if not tmp == "":
            tmp = ", " + tmp
        return "{0}{1}".format(self.last_name, tmp)


# obiekt wypożyczenia
class Rent(models.Model):
    # opis, notatka
    description = models.TextField(blank=True)
    # wypożyczony od (data)
    from_date = models.DateField(default=timezone.now)
    # wypożyczony do (data) zadeklarowane przed oddaniem/ustawione na dzień oddania
    to_date = models.DateField()
    # klucz obcy na pojazd
    vehicle = models.ForeignKey(Vehicle, on_delete=models.DO_NOTHING)
    # klucz obcy na wypożyczającego
    renter = models.ForeignKey(Renter, on_delete=models.DO_NOTHING)
    # flaga czy aktualnie wypożyczony
    rented = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return "{0} - {1}: {3}, {4}. {2}".format(self.from_date,
                                                 self.to_date,
                                                 self.description,
                                                 self.vehicle,
                                                 self.renter)

    # dodatkowe prawa dostępu
    class Meta:
        permissions = (("can_mark_returned", "Can mark rent as returned"),
                       ("can_show_week", "Can show week view"),
                       )

    # Zwraca True gdy pojazd nie oddany a minęła data wypożyczenia
    def is_not_bring_back(self) -> bool:
        return self.to_date < timezone.now().date() and self.from_date < timezone.now().date() and self.rented == 1
