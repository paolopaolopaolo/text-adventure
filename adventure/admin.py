from django.contrib import admin
from adventure.models import Story, Scene, Agent, Move, Inventory
from django.utils.translation import ugettext_lazy as _


class AgentTypeFilter(admin.SimpleListFilter):
    title = _('agent type')
    parameter_name = 'agenttype'

    def lookups(self, request, model_admin):
        return (
            ('enemy', _('is an enemy agent')),
            ('enemy_primitive', _('is an enemy agent (primitive)')),
            ('player', _('is a player agent')),
            ('npc', _('is a npc agent')),
            ('npc_primitive', _('is a npc agent (primitive)')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'enemy':
            return queryset.filter(type='EN')
        if self.value() == 'enemy_primitive':
            return queryset.filter(type='EN', scene=None)
        if self.value() == 'player':
            return queryset.filter(type='PLR')
        if self.value() == 'npc_primitive':
            return queryset.filter(type='NPC', scene=None)


class MovePrimitivesFilter(admin.SimpleListFilter):
    title = _('move primitive')
    parameter_name = 'inventoryprimitive'

    def lookups(self, request, model_admin):
        return (
            ('primitive', _('is a move primitive')),
            ('not primitive', _('is not a move primitive')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'primitive':
            return queryset.filter(user=None)
        elif self.value() == 'not primitive':
            return queryset.exclude(user=None)


class InventoryPrimitivesFilter(admin.SimpleListFilter):
    title = _('inventory primitive')
    parameter_name = 'inventoryprimitive'

    def lookups(self, request, model_admin):
        return (
            ('primitive', _('is an inventory primitive')),
            ('not primitive', _('is not an inventory primitive')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'primitive':
            return queryset.filter(found_location=None, owner=None)
        elif self.value() == 'not primitive':
            return queryset.exclude(found_location=None, owner=None)


class InventoryAdmin(admin.ModelAdmin):
    list_filter = (InventoryPrimitivesFilter,)


class MoveAdmin(admin.ModelAdmin):
    list_filter = (MovePrimitivesFilter,)


class AgentAdmin(admin.ModelAdmin):
    list_filter = (AgentTypeFilter,)

# Register your models here.
admin.site.register(Agent, AgentAdmin)
admin.site.register(Move, MoveAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Story)
admin.site.register(Scene)
