from django.contrib import admin
from adventure.models import Agent, Move, Inventory

# Register your models here.
admin.site.register(Agent)
admin.site.register(Move)
admin.site.register(Inventory)
