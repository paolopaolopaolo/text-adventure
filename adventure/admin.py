from django.contrib import admin
from adventure.models import Story, Scene, Agent, Move, Inventory

# Register your models here.
admin.site.register(Agent)
admin.site.register(Move)
admin.site.register(Inventory)
admin.site.register(Story)
admin.site.register(Scene)
