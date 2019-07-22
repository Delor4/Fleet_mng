from django.contrib import admin

from .models import Vehicle, Rent, Renter

admin.site.register(Vehicle)
admin.site.register(Renter)
admin.site.register(Rent)
