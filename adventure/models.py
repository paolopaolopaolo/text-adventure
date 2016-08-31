from django.db import models
from django.forms.models import model_to_dict


MOVE_EFFECT_TYPES = (
    ('HP', 'HP Effect'),
    ('HPS', 'HP Stat Effect'),
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


class Agent(models.Model):
    name = models.CharField(max_length=50, default='')
    description = models.CharField(max_length=100, default='')
    type = models.CharField(max_length=3, choices=AGENT_TYPES)
    attack_dmg = models.IntegerField()
    spc_attack_dmg = models.IntegerField()
    hp = models.IntegerField()
    mp = models.IntegerField()

    def _nativize_move(self, move):
        compare_fields = [
            'name',
            'description',
            'type',
            'effect_magnitude',
            'special_move'
        ]
        move = model_to_dict(move, fields=compare_fields)
        return move

    def knows_move(self, move):
        move = self._nativize_move(move)
        current_moves = [self._nativize_move(current_move) for current_move in self.moves.all()]
        return move in current_moves

    def learn_move(self, move):
        if not self.knows_move(move):
            new_move = Move.objects.get(id=move.id)
            new_move.id = None
            new_move.user = self
            new_move.save()

    def use_move(self, entity, move):
        assert isinstance(entity, Agent)


class Move(models.Model):
    name = models.CharField(max_length=50, default='')
    description = models.CharField(max_length=100, default='')
    special_move = models.BooleanField(default=False)
    type = models.CharField(max_length=3, choices=MOVE_EFFECT_TYPES)
    effect_magnitude = models.IntegerField()
    user = models.ForeignKey("Agent", related_name='moves', null=True, blank=True)


class Inventory(models.Model):
    type = models.CharField(max_length=3, choices=INVENTORY_TYPE)
