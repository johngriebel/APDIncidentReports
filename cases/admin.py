from django.contrib import admin

from .models import Officer, Offense, Address

admin.site.register(Officer)
admin.site.register(Offense)
admin.site.register(Address)
