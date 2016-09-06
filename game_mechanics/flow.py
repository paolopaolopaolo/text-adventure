from adventure.models import Agent, Story, Move, Inventory
import os
import re
import random


class MenuItem:

    def __init__(self, *args):
        self.name, self.method = args


class FlowRunner:

    def __init__(self):
        self.adventure = None
        self.character = None

    def choose_story(self):
        stories = Story.objects.all()
        story_choice = self.menuify_queryset(stories,
                                             'Adventure Name:')
        if story_choice:
            self.adventure = story_choice
        else:
            self.choose_story()

    def create_character(self):
        move_choice = []
        excluded_moves = []
        name = input('What is your character\'s name?: ')
        if Agent.objects.filter(type='PLR', name=name).count() > 0:
            continue_game = input('Continue Game (y/n)?: ').lower()
            if continue_game == 'y':
                print('Confirm which character you\'re loading.')
                self.character = self.menuify_queryset(
                    Agent.objects.filter(type='PLR', name=name).all(),
                    'Agent:\tDescription:',
                    'description'
                )
        else:
            description = input('Tell us about this character: ')
            character = Agent(type='PLR',
                              name=name,
                              description=description,
                              hp=100,
                              mp=10,
                              attack_dmg=0,
                              spc_attack_dmg=0)
            character.save()

            while len(move_choice) < 3:
                random_moves = Move.objects\
                                   .filter(user=None)\
                                   .exclude(id__in=excluded_moves)\
                                   .all()
                move = self.menuify_queryset(
                    random_moves,
                    'Move Name:\tType:\tEffect:\tIsSpecial:',
                    'type',
                    'effect_magnitude',
                    'special_move'
                )
                if move:
                    move_choice.append(move)
                    excluded_moves.append(move.id)
            for move in move_choice:
                character.learn_move(move)
            self.character = character

    @classmethod
    def print_header(cls, word):
        print('##{}##'.format('=' * (len(word))))

    def start(self):
        self.print_header(self.adventure.name)
        print('  {}'.format(self.adventure.name))
        self.print_header(self.adventure.name)
        print(self.adventure.description)
        print('.' * 20)
        if self.character.scene is None:
            self.character.scene = self.adventure.first_scene
            self.character.save()
        self.main_loop()

    @classmethod
    def menuify_queryset(cls, queryset, header_value, *args, use_header=True):
        keys = []
        if use_header:
            header = 'Option:\t{}'.format(header_value)
        else:
            header = ''
        for idx, item in enumerate(queryset):
            other_args = [getattr(item, attr) for attr in args]
            values = [idx, item.name]
            values.extend(other_args)
            header = '\n'.join((
                header,
                '\t'.join([str(value) for value in values])
            ))
            keys.append(item)
        print(header)
        choice = input('Choice (use option #): ')
        try:
            choice = int(choice)
        except ValueError:
            choice = None
        if choice is not None:
            try:
                chosen_item = keys[choice]
                os.system('clear')
                return chosen_item
            except IndexError:
                print('No option')
        os.system('clear')
        return

    def navigate(self):
        all_scenes = [scene for scene in self.character.scene.to_scenes.all()]
        all_scenes.extend([scene for scene in self.character.scene.from_scenes.all()])
        choice = self.menuify_queryset(
            all_scenes,
            'Path to:'
        )
        if choice is not None:
            self.character.scene = choice
            self.character.save()

    def check_thyself(self):
        print("""
----------
USER STATS
----------
name: {}
description: {}
hp: {}
mp: {}
special attack: {}
attack: {}
""".format(self.character.dict['name'],
           self.character.dict['description'],
           self.character.dict['hp'],
           self.character.dict['mp'],
           self.character.dict['spc_attack_dmg'],
           self.character.dict['attack_dmg'],
           ))

    def use_one_of(self, items, character):
        def item_use_method():
            return (character.use_inventory(items[-1]),
                    items[-1].type,
                    items[-1].description)
        return item_use_method

    def take_one_of(self, items, character):
        def item_take_method():
            return (character.take_inventory(items[-1]),
                    items[-1].type,
                    items[-1].description)
        return item_take_method

    def compress_inventory_menu(self, inventories, character, callback_method):
        # INPUT:Takes list of inventories
        # OUTPUT: Returns mixed list of Menu items and inventory items
        result = []
        # Take item list and hash into dictionary
        inventory_hash = {}
        for inventory in inventories:
            inventory_key = "{}.{}.{}".format(inventory.name,
                                              inventory.type,
                                              inventory.effect_magnitude)
            if inventory_key in list(inventory_hash.keys()):
                inventory_hash[inventory_key].append(inventory)
            else:
                inventory_hash[inventory_key] = [inventory]
        # Iterate through dictionary (checking value)
        for inv_key, inv_value in inventory_hash.items():
            if len(inv_value) > 1:
                # If value is greater than one, append a MenuItem
                result.append(MenuItem(inv_key.split('.')[0]+"({})".format(len(inv_value)),
                                       callback_method(inv_value, character)))
            elif len(inv_value) == 1:
                # If value is equal to one, append the inventory
                result.append(inv_value[0])
        return result

    def check_inventory(self):
        owned_items = self.compress_inventory_menu(self.character.agent_items.all(),
                                                   self.character,
                                                   self.use_one_of)
        if self.character.agent_items.filter(inventory_type='CNS').all().count() > 0:
            owned_items.append(MenuItem('Use all items', self.use_all_items))
        if len(owned_items) == 0:
            print('++++++++++++++++++++++++')
            print('You have no items')
            print('++++++++++++++++++++++++')
            return
        item_to_use = self.menuify_queryset(owned_items,
                                            'Item:')
        if item_to_use is not None:
            if not isinstance(item_to_use, MenuItem):
                print('='*len(item_to_use.description.split('\\n')[0]))
                print(re.sub(r'\\n', '\n', item_to_use.description))
                print('='*len(item_to_use.description.split('\\n')[0]))
                self.character.use_inventory(item_to_use)
            else:
                if item_to_use.name == 'Use all items':
                    import pdb; pdb.set_trace()
                    item_to_use.method()
                else:
                    effect, _, description = item_to_use.method()
                    print('='*len(description.split('\\n')[0]))
                    print(re.sub(r'\\n', '\n', description))
                    print('='*len(description.split('\\n')[0]))
            self.check_inventory()
        else:
            return

    def add_all_items(self):
        for item in self.character.scene.scene_items.all():
            self.character.take_inventory(item)

    def use_all_items(self):
        users_items = self.character.agent_items.filter(inventory_type='CNS').all()
        for item in users_items:
            self.character.use_inventory(item)
        users_items.delete()

    def find_items(self):
        items = self.compress_inventory_menu([it for it in self.character.scene.scene_items.order_by('id').all()],
                                             self.character,
                                             self.take_one_of)
        items.append(MenuItem('All', self.add_all_items))
        if self.character.scene.scene_items.count() == 0:
            print('++++++++++++++++++++++++')
            print('There are no items here.')
            print('++++++++++++++++++++++++')
            return
        item = self.menuify_queryset(items,
                                     'Item:')
        if item is not None:
            if item.name == 'All' or isinstance(item, MenuItem):
                item.method()
            else:
                self.character.take_inventory(item)
            self.find_items()
        else:
            return

    def fight_enemy(self, player, enemy):
        def combat_loop():
            actors = [enemy, player]
            random.shuffle(actors)
            current_actor_idx = 0
            move_lock = False
            print("You engage {} in a combat sequence TO THE DEATH".format(enemy.name))
            while player.hp > 0 and enemy.hp > 0:
                # Current actor uses move
                current_actor = actors[current_actor_idx]
                if current_actor.type == 'EN':
                    move = random.choice(current_actor.moves.all())
                    if move.effect_magnitude < 0:
                        effect = current_actor.use_move(player, move)
                        print("{} uses {}!".format(current_actor.name, move.name))
                        print(re.sub(r'\\n', '\n', move.description))
                        print("Your {} stat is decreases by {}!".format(move.type, effect))
                    else:
                        effect = current_actor.use_move(enemy, move)
                        print("{} uses {}!".format(current_actor.name, move.name))
                        print(re.sub(r'\\n', '\n', move.description))
                        print("{}'s {} stat increases by {}!".format(enemy.name, move.type, effect))
                else:
                    potential_moves = [move for move in player.moves.all()]
                    potential_items = self.compress_inventory_menu([item for item in player.agent_items.all()],
                                                                   player,
                                                                   self.use_one_of)
                    potential_moves.extend(potential_items)
                    move = self.menuify_queryset(potential_moves,
                                                 "Move/Item:")
                    if isinstance(move, Move):
                        if move.effect_magnitude < 0:
                            effect = current_actor.use_move(enemy, move)
                            print("You use {}!".format(move.name))
                            print(re.sub(r'\\n', '\n', move.description))
                            print("{}'s {} stat is decreases by {}!".format(enemy.name,
                                                                            move.type,
                                                                            effect))
                        else:
                            effect = current_actor.use_move(current_actor, move)
                            print("You use {}!".format(move.name))
                            print(re.sub(r'\\n', '\n', move.description))
                            print("Your {} stat increases by {}!".format(move.type,
                                                                         effect))
                    if isinstance(move, Inventory):
                        effect = current_actor.use_inventory(move)
                        print("You use {}!".format(move.name))
                        print(re.sub(r'\\n', '\n', move.description))
                        print("Your {} stat increases by {}!".format(move.type,
                                                                     effect))
                    if isinstance(move, MenuItem):
                        effect, type, description = move.method()
                        print("You use {}!".format(move.name))
                        print(re.sub(r'\\n', '\n', description))
                        print("Your {} stat increases by {}!".format(type, effect))

                    move_lock = move is None

                if not move_lock:
                    print('Your HP: {}\nEnemy HP: {}'.format(player.hp, enemy.hp))
                    # Toggle current actor
                    if current_actor_idx:
                        current_actor_idx = 0
                    else:
                        current_actor_idx = 1
            if player.hp <= 0:
                print("You lost!")
            if enemy.hp <=0:
                print("You won!")
        return combat_loop

    def main_loop(self):

        while self.character.hp > 0:
            menu_items = [
                MenuItem('Navigate', self.navigate),
                MenuItem('Check stats', self.check_thyself),
                MenuItem('Use Inventory', self.check_inventory),
                MenuItem('Look for items', self.find_items),
            ]
            enemies = self.character.scene.agents.filter(type='EN', hp__gt=0)
            if enemies.count() > 0:
                menu_items.pop(0)
                for enemy in enemies:
                    menu_items.append(MenuItem('Fight {}'.format(enemy.name), self.fight_enemy(self.character, enemy)))

            print(self.character.scene.complete_description)
            print('')
            agent_description = self.character.scene.agent_description(self.character)
            if agent_description:
                print(agent_description)
            choice = self.menuify_queryset(
                menu_items,
                'Actions:'
            )
            if choice:
                choice.method()
        self.character.delete()
        print('GAME OVER')
        print('Play again(y/n)?')
        again = input('').lower()
        if again == 'y':
            self.initiate_flow()

    def random_scene(self):
        scenes = [scene for scene in self.adventure.scenes.exclude(id=self.adventure.first_scene.id).all()]
        scene_choice = random.choice(scenes)
        return scene_choice

    def random_enemy(self):
        enemy_pool = Agent.objects\
                          .filter(type='EN',
                                  scene=None,
                                  is_boss=False)
        enemies = [enem for enem in enemy_pool.all()]
        enemy_choice = random.choice(enemies)
        return enemy_choice

    def learn_random_moveset(self, enemy):
        move_choice = []
        excluded_moves = []
        while len(move_choice) < 2:
            moves = Move.objects\
                        .filter(user=None)\
                        .exclude(id__in=excluded_moves)\
                        .all()
            move = moves.order_by('?').first()
            move_choice.append(move)
            excluded_moves.append(move.id)
        for move in move_choice:
            enemy.learn_move(move)

    def add_enemies(self, num_enemies=5):
        # Clear enemies
        for scene in self.adventure.scenes.all():
            scene.agents.filter(type='EN').all().delete()
        # Add random enemies to random scenes
        for times in range(num_enemies):
            random_enemy = self.random_enemy()
            self.learn_random_moveset(
                self.random_scene().add_enemy(random_enemy)
            )

    def sprinkle_inventory(self, num_inventory=5):
        for scene in self.adventure.scenes.all():
            scene.scene_items.all().delete()
        for times in range(num_inventory):
            random_inventory = Inventory.objects.filter(found_location=None, owner=None).order_by('?').first()
            random_scene = self.adventure.scenes.order_by('?').first()
            random_scene.add_inventory(random_inventory)

    def initiate_flow(self):
        try:
            self.choose_story()
            os.system('clear')
            self.create_character()
            reset_game = input('Reset game? (y/n): ').lower()
            if reset_game == 'y':
                lowrange = self.adventure.scenes.count() - 2
                highrange = self.adventure.scenes.count()
                try:
                    density = float(input('Enemy Density? (~# of enemies per scene): '))
                except ValueError:
                    density = 0.75
                enemy_count = random.randrange(int(density*lowrange), int(density*highrange))
                self.add_enemies(num_enemies=enemy_count)
                try:
                    density = float(input('Item Density? (~# of items per scene): '))
                except ValueError:
                    density = 2.0
                inventory_count = random.randrange(int(density*lowrange), int(density*highrange))
                self.sprinkle_inventory(inventory_count)
            os.system('clear')
            self.start()
        except KeyboardInterrupt:
            self.initiate_flow()

if __name__ == '__main__':
    flow = FlowRunner()
    flow.initiate_flow()
