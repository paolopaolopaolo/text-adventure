from django.db import models

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

    def learn_move(self, move):
        new_move = Move.objects.get(id=move.id)
        new_move.id = None
        new_move.user = self
        new_move.save()


class Move(models.Model):
    name = models.CharField(max_length=50, default='')
    description = models.CharField(max_length=100, default='')
    special_move = models.BooleanField(default=False)
    type = models.CharField(max_length=3, choices=MOVE_EFFECT_TYPES)
    effect_magnitude = models.IntegerField()
    user = models.ForeignKey("Agent", related_name='moves', null=True, blank=True)


class Inventory(models.Model):
    type = models.CharField(max_length=3, choices=INVENTORY_TYPE)
