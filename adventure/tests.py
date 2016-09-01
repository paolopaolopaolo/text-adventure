from django.test import TestCase
from adventure.models import Agent, Move, Inventory, Scene


class AdventureTestCase(TestCase):

    def setUp(self):
        player_stats = {
            'type': 'PLR',
            'name': 'Mr. Snuffles',
            'description': 'He was abandoned as a pup.',
            'attack_dmg': 10,
            'spc_attack_dmg': 20,
            'hp': 100,
            'mp': 5,
        }
        enemy_stats = {
            'type': 'EN',
            'name': 'The Octopus Man',
            'description': 'Once ate a whole village.',
            'attack_dmg': 5,
            'spc_attack_dmg': 100,
            'hp': 100,
            'mp': 5,
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
            'effect_magnitude': -20,
            'special_move': True
        }
        move_stats3 = {
            'name': 'The world\'s smallest hug',
            'description': 'So annoying! Nothing you can do about it though',
            'type': 'HP',
            'effect_magnitude': 10,
            'special_move': True
        }
        inventory1_kwargs = {
            'name': 'A rock',
            'description': 'A small, handy piece of earth',
            'inventory_type': 'CNS',
            'type': 'SAD',
            'effect_magnitude': 10
        }
        inventory2_kwargs = {
            'name': 'A small peanut candy',
            'description': 'It was forged in a delicious fire',
            'inventory_type': 'CNS',
            'type': 'HP',
            'effect_magnitude': 2
        }
        scene1_kwargs = {
            'name': 'The Lake',
            'description': 'It is wet and hot. There are bees in the distance.',
        }
        scene2_kwargs = {
            'name': 'The Porridge Palace',
            'description': 'Porridge lines the walls and roof of this monument to hubris.',
        }
        self.scene1 = Scene(**scene1_kwargs)
        self.scene2 = Scene(**scene2_kwargs)
        self.scene1.save()
        self.scene2.save()
        self.player = Agent(**player_stats)
        self.player.save()
        self.enemy = Agent(**enemy_stats)
        self.enemy.save()
        self.move1 = Move(**move_stats1)
        self.move2 = Move(**move_stats2)
        self.move3 = Move(**move_stats3)
        self.move1.save()
        self.move2.save()
        self.move3.save()
        self.inventory1 = Inventory(**inventory1_kwargs)
        self.inventory2 = Inventory(**inventory2_kwargs)
        self.inventory1.save()
        self.inventory2.save()

    def test_learn_move(self):
        self.assertEqual(Move.objects.all().count(), 3)
        # Player learns a move
        self.player.learn_move(self.move1)
        self.assertEqual(Move.objects.all().count(), 4)
        self.assertEqual(self.player.moves.count(), 1)
        self.assertEqual(self.player.moves.first().name, 'Death stroke')
        # Noop, if player already knows move
        self.player.learn_move(self.move1)
        self.assertEqual(Move.objects.all().count(), 4)
        self.assertEqual(self.player.moves.count(), 1)
        # Learn another move
        self.player.learn_move(self.move2)
        self.assertEqual(Move.objects.all().count(), 5)
        self.assertEqual(self.player.moves.count(), 2)

    def test_knows_move(self):
        # User knows moves
        self.assertEqual(self.player.knows_move(self.move1), False)
        self.assertEqual(self.player.knows_move(self.move2), False)
        # Learn one move
        self.player.learn_move(self.move1)
        self.assertEqual(self.player.knows_move(self.move1), True)
        self.assertEqual(self.player.knows_move(self.move2), False)
        # Learn another move
        self.player.learn_move(self.move2)
        self.assertEqual(self.player.knows_move(self.move1), True)
        self.assertEqual(self.player.knows_move(self.move2), True)

    def test_use_move(self):
        self.player.learn_move(self.move1)
        # Enemy: 100 HP
        # Player: 10 Atk.Dmg
        # Move: -10 Dmg
        # Damage: 1.10 * -10 + 100 = 89
        self.player.use_move(self.enemy, 0)
        self.assertEqual(self.enemy.hp, 89)
        self.enemy.learn_move(self.move2)
        # Player: 100 HP
        # Enemy: 100 Spc.Atk.Dmg
        # Move: -20 Dmg
        # Damage: 2.0 * -20+ 100 = 60
        self.enemy.use_move(self.player, 0)
        self.assertEqual(self.enemy.mp, 4)
        self.assertEqual(self.player.hp, 60)
        self.player.learn_move(self.move3)
        # Player: 60 HP
        # Player: 20 Spc.Atk.Dmg
        # Move: 10 HP
        # Action: 1.20 * 10 + 60 = 72
        self.player.use_move(self.player, 1)
        self.assertEqual(self.player.mp, 4)
        self.assertEqual(self.player.hp, 72)
        # Player: 72 HP
        # Player: 20 Spc.Atk.Dmg
        # Move: 10 HP
        # Action: 1.20 * 10 + 72 = 84
        self.player.use_move(self.player, 1)
        self.assertEqual(self.player.mp, 3)
        self.assertEqual(self.player.hp, 84)

    def test_take_inventory(self):
        self.scene1.add_inventory(self.inventory1)
        self.scene1.add_inventory(self.inventory1)
        self.scene1.add_inventory(self.inventory1)
        self.scene1.add_inventory(self.inventory2)
        self.assertEqual(Inventory.objects.count(), 6)
        self.player.scene = self.scene1
        rocks = self.scene1.scene_items.filter(name__contains='rock')
        candy = self.scene1.scene_items.filter(name__contains='peanut')
        self.assertEqual(len(rocks), 3)
        self.assertEqual(len(candy), 1)
        self.assertEqual(self.scene1.scene_items.last().name, 'A small peanut candy')
        self.player.take_inventory(3)
        self.assertEqual(self.player.owns_item(self.inventory1), False)
        self.assertEqual(self.player.owns_item(self.inventory2), True)
        self.assertEqual(self.scene1.scene_items.last().name, 'A rock')


