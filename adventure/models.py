from django.db import models
from django.forms.models import model_to_dict
from game_mechanics.turns import apply_move

MOVE_EFFECT_TYPES = (
    ('HP', 'HP Effect'),
    ('MP', 'MP Effect'),
    ('AD', 'Attack Damage Effect'),
    ('SAD', 'Special Attack Damage Effect'),
)

AGENT_TYPES = (
    ('EN', 'enemy'),
    ('NPC', 'npc'),
    ('PLR', 'player')
)

INVENTORY_TYPE = (
    ('CNS', 'consumable'),
    ('KI', 'key item'),
)

# Abstract (non-migrated) models


class NamedModel(models.Model):
    name = models.CharField(max_length=50, default='')
    description = models.CharField(max_length=100, default='')
    compare_fields = []

    class Meta:
        abstract = True

    @property
    def dict(self):
        if len(self.compare_fields) > 0:
            compare_fields = self.compare_fields
        else:
            compare_fields = [field.name for field in self._meta.get_fields()]
        dict_item = model_to_dict(self, fields=compare_fields)
        return dict_item


class StatChanger(NamedModel):
    type = models.CharField(max_length=3, choices=MOVE_EFFECT_TYPES)
    effect_magnitude = models.IntegerField()

    class Meta:
        abstract = True

# Actual Models


class Agent(NamedModel):
    type = models.CharField(max_length=3, choices=AGENT_TYPES)
    attack_dmg = models.IntegerField()
    spc_attack_dmg = models.IntegerField()
    hp = models.IntegerField()
    mp = models.IntegerField()
    scene = models.ForeignKey('Scene', related_name='agents', null=True)

    def knows_move(self, move):
        move = move.dict
        current_moves = [current_move.dict for current_move in self.moves.all()]
        return move in current_moves

    def owns_item(self, inventory):
        inventory = inventory.dict
        current_invs = [current_inv.dict for current_inv in self.agent_items.all()]
        return inventory in current_invs

    def learn_move(self, move):
        if not self.knows_move(move):
            new_move = Move.objects.get(id=move.id)
            new_move.id = None
            new_move.user = self
            new_move.save()

    def use_move(self, entity, idx):
        move = self.moves.all().order_by('id')[idx]
        apply_move(self, entity, move)

    def take_inventory(self, idx):
        inventory = self.scene.scene_items.all().order_by('id')[idx]
        inventory.owner = self
        inventory.found_location = None
        inventory.save()

    def use_inventory(self, idx):
        item = self.agent_items.all().order_by('id')[idx]
        apply_move(self, self, item)
        item.delete()


class Move(StatChanger):
    user = models.ForeignKey("Agent", related_name='moves', null=True, blank=True)
    special_move = models.BooleanField(default=False)
    compare_fields = [
        'name',
        'description',
        'type',
        'effect_magnitude',
        'special_move'
    ]


class Inventory(StatChanger):
    inventory_type = models.CharField(max_length=3, choices=INVENTORY_TYPE)
    compare_fields = [
        'name',
        'description',
        'type',
        'inventory_type',
        'effect_magnitude',
    ]
    found_location = models.ForeignKey("Scene", related_name='scene_items', null=True)
    owner = models.ForeignKey("Agent", related_name='agent_items', null=True)


class Scene(NamedModel):
    to_scenes = models.ManyToManyField("self", related_name='from_scenes', symmetrical=False, blank=True)

    @property
    def complete_description(self):
        string_description = "You find yourself at {}. {}\n".format(self.name, self.description)
        if self.to_scenes.count() > 0:
            for idx, scene in enumerate(self.to_scenes.all()):
                if idx == 0:
                    prefix = "In one direction, "
                else:
                    prefix = "In another, "
                string_description = "".join((
                    string_description,
                    prefix,
                    "is the path to {}. ".format(scene.name)
                ))
            for idx, fscene in enumerate(self.from_scenes.all()):
                if idx == 0:
                    prefix = "Turning around, one way "
                else:
                    prefix = "Another way "
                string_description = "".join((
                    string_description,
                    prefix,
                    "leads back to {}. ".format(fscene.name)
                ))
        return string_description

    def add_inventory(self, inventory):
        new_item = Inventory.objects.get(id=inventory.id)
        new_item.id = None
        new_item.found_location = self
        new_item.save()
