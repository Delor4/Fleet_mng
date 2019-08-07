from django.contrib.admin.models import LogEntry, ADDITION, DELETION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver


class TraceableModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    additional_data = {}

    class Meta:
        abstract = True


# dane pojazdu
class Vehicle(TraceableModel):
    # nazwa pojazdu
    name = models.CharField(max_length=193, db_index=True)

    # marka, model, wersja
    brand = models.CharField(max_length=193)
    model = models.CharField(max_length=193)
    generation = models.CharField(max_length=193, blank=True)
    # nr rej.
    registration_number = models.CharField(max_length=193)
    # przebieg
    mileage = models.CharField(blank=True, max_length=20, default="0")
    # badania techniczne
    checkup = models.DateField(blank=True, null=True)
    # ubezpieczenie
    insurance = models.DateField(blank=True, null=True)

    # dłuższy opis
    description = models.TextField(blank=True)

    deleted = models.BooleanField(default=False)

    # ciąg znaków opisujący obiekt
    def __str__(self) -> str:
        return "{0} {1}".format(self.brand, self.registration_number)

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

    def get_str(self):
        return str([[self.name,
                     self.brand,
                     self.model,
                     self.generation
                     ],
                    [self.registration_number,
                     self.mileage],
                    [{'checkup': self.checkup,
                      'insurance': self.insurance,
                      }],
                    [{'deleted': self.deleted,
                      'description': self.description,
                      }]
                    ])


# Wypożyczający
class Renter(TraceableModel):
    # krótka nazwa
    last_name = models.CharField(max_length=193)
    first_name = models.CharField(max_length=193, blank=True)
    # dłuższy opis
    description = models.TextField(blank=True)

    deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        tmp = self.first_name
        if not tmp == "":
            tmp = ", " + tmp
        return "{0}{1}".format(self.last_name, tmp)

    def get_str(self):
        return str([self.last_name,
                    self.first_name,
                    self.description,
                    self.deleted,
                    ],
                   )


# obiekt wypożyczenia
class Rent(TraceableModel):
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

    deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return "{0} - {1}: {3}, {4}.".format(self.from_date,
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

    def get_str(self):
        return str([self.from_date,
                    self.to_date,
                    self.vehicle.id,
                    self.renter.id,
                    self.description,
                    self.rented,
                    self.deleted,
                    ],
                   )


def log_user_entry(request, obj, action_flag, msg):
    LogEntry.objects.log_action(
        user_id=request.user.id,
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=str({'username': obj.username,
                         'groups': [gr.id for gr in obj.groups.all()],
                         'is_active': obj.is_active,
                         }),
        action_flag=action_flag,
        change_message=msg)


def log_entry(model: TraceableModel, action_flag):
    user_id = 1
    msg = '[Unknown user.]' + model.get_str()
    if model.additional_data:
        user_id = model.additional_data['request'].user.id
        msg = model.get_str()
    LogEntry.objects.log_action(
        user_id=user_id,
        content_type_id=ContentType.objects.get_for_model(model).pk,
        object_id=model.pk,
        object_repr=msg,
        action_flag=action_flag,
    )


@receiver(post_save)
def post_save_handler(sender, instance, created, using, **kwargs):
    if isinstance(instance, TraceableModel):
        if created:
            log_entry(instance, ADDITION)
        else:
            log_entry(instance, CHANGE)


@receiver(post_delete)
def post_delete_handler(sender, instance, using, **kwargs):
    if isinstance(instance, TraceableModel):
        log_entry(instance, sender, DELETION, "")
