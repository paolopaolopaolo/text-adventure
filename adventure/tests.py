from django.test import TestCase
from adventure.models import Agent, Move, Inventory


class AdventureTestCase(TestCase):

    def setUp(self):
        player_stats = {
            'type': 'PLR',
            'name': 'Mr. Snuffles',
            'description': 'He was abandoned as a pup.',
            'attack_dmg': 2,
            'spc_attack_dmg': 10,
            'hp': 10,
            'mp': 2,
        }
        enemy_stats = {
            'type': 'EN',
            'name': 'The Octopus Man',
            'description': 'Once ate a whole village.',
            'attack_dmg': 5,
            'spc_attack_dmg': 1,
            'hp': 6,
            'mp': 0,
        }
        move_stats1 = {
            'name': 'Death stroke',
            'description': 'High-fiving the Grim Reaper, which is the only way to get his attention',
            'type': 'HP',
            'effect_magnitude': -10,
            'special_move': False
        }
        move_stats2 = {
            'name': 'Grip of Doom',
            'description': 'Each finger compresses with the force of a small sedan',
            'type': 'HP',
            'effect_magnitude': -100,
            'special_move': True
        }
        self.player = Agent(**player_stats)
        self.player.save()
        self.enemy = Agent(**enemy_stats)
        self.enemy.save()
        self.move1 = Move(**move_stats1)
        self.move2 = Move(user=self.player, **move_stats2)
        self.move1.save()
        self.move2.save()

    def test_learn_move(self):
        self.player.learn_move(self.move1)
        self.assertEqual(Move.objects.all().count(), 3)
        self.assertEqual(self.player.moves.count(), 2)
        self.assertEqual(self.player.moves.first().name, 'Grip of Doom')
        self.assertEqual(self.player.moves.last().name, 'Death stroke')
        # Noop, if player already knows move
        self.player.learn_move(self.move1)
        self.assertEqual(Move.objects.all().count(), 3)
        self.assertEqual(self.player.moves.count(), 2)

    def test_knows_move(self):
        self.assertEqual(self.player.knows_move(self.move1), False)
        self.assertEqual(self.player.knows_move(self.move2), True)
        self.player.learn_move(self.move1)
        self.assertEqual(self.player.knows_move(self.move1), True)

    def test_use_move(self):
        pass
