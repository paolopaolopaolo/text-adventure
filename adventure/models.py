from django.db import models
from django.forms.models import model_to_dict
from game_mechanics.turns import apply_move, apply_item

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
    description = models.CharField(max_length=1000, default='')
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

    def __str__(self):
        return self.name


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
    is_boss = models.BooleanField(default=False)
    hp = models.IntegerField()
    mp = models.IntegerField()
    scene = models.ForeignKey('Scene', related_name='agents', null=True, blank=True)

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

    def use_move(self, entity, move):
        effect = apply_move(self, entity, move)
        return effect

    def show_inventory(self):
        print("INVENTORY:")
        for item in self.agent_items.all():
            print("="*len(item.name))
            print(item.name)
            print("="*len(item.name))
            print("{}:{}".format(item.type,
                                 item.effect_magnitude))
            print("")

    def take_inventory(self, inventory):
        inventory.owner = self
        inventory.found_location = None
        inventory.save()

    def use_inventory(self, item):
        effect = apply_item(self, item)
        item.delete()
        return effect


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
    found_location = models.ForeignKey("Scene", related_name='scene_items', null=True, blank=True)
    owner = models.ForeignKey("Agent", related_name='agent_items', null=True, blank=True)


class Scene(NamedModel):
    to_scenes = models.ManyToManyField("self", related_name='from_scenes', symmetrical=False, blank=True)
    story = models.ForeignKey('Story', related_name='scenes', null=True, blank=True)

    def _render_scene_attribute(self, attributes, prefix_dict, identifier_strings, starting_string):
        for attribute in attributes:
            queryset = getattr(self, attribute).all()
            for idx, item in enumerate(queryset.all()):
                if idx == 0:
                    prefix = prefix_dict.get(attribute)[0]
                else:
                    prefix = prefix_dict.get(attribute)[1]
                starting_string = ''.join((
                    starting_string,
                    prefix,
                    identifier_strings.get(attribute).format(item.name)
                ))
        return starting_string

    def agent_description(self, current_agent):
        other_agents = self.agents.exclude(id=current_agent.id).filter(hp__gt=0).all()
        if other_agents.count() > 0:
            message = "\n".join((
                "=" * 26,
                "You see other people here.",
                "=" * 26,
                ""
            ))
            for agent in other_agents:
                message = "\n".join((
                    message,
                    "%" * len(agent.name),
                    agent.name,
                    "-" * len(agent.name),
                    agent.description,
                    ''
                ))
            return message
        return

    @property
    def inventory_description(self):
        item_description = "\n".join((
            "=" * 24,
            "There are items here.",
            "=" * 24,
            ""
        ))
        item_hash = {}
        for item in self.scene_items.all():
            if item.name in list(item_hash.keys()):
                item_hash[item.name] += 1
            else:
                item_hash[item.name] = 1
        for item_name, item_number in item_hash.items():
            item_obj = self.scene_items.filter(name=item_name).first()
            item_description = "\n".join((
                item_description,
                "%" * (len(item_obj.name) + 5),
                "{} ({})".format(item_obj.name, item_number),
                "-" * (len(item_obj.name) + 5),
                'Affects: {}'.format(item_obj.type),
                'By: {}'.format(item_obj.effect_magnitude),
                ''
            ))
        if self.scene_items.count() > 0:
            return item_description
        return ""

    def add_enemy(self, enemy):
        enemy_copy = enemy
        enemy_copy.id = None
        enemy_copy.scene = self
        enemy_copy.save()
        return enemy_copy

    @property
    def complete_description(self):
        string_description = "You find yourself at {}. {}\n".format(self.name, self.description)
        prefixes = {
            'to_scenes': ('In one direction ', 'In another, '),
            'from_scenes': ('Turning around, one way ', 'Another way '),
        }
        identifier_strings = {
            'to_scenes': 'is the path to {}. ',
            'from_scenes': 'leads back to {}. ',
        }
        string_description = self._render_scene_attribute(
            ['to_scenes', 'from_scenes'],
            prefixes,
            identifier_strings,
            string_description
        )
        return string_description

    def add_inventory(self, inventory):
        new_item = Inventory.objects.get(id=inventory.id)
        new_item.id = None
        new_item.found_location = self
        new_item.save()


class Story(NamedModel):
    first_scene = models.ForeignKey(Scene, related_name='stories')
