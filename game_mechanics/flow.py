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

    @classmethod
    def y_or_n_question(cls, prompt):
        answer = input('{} (y/n)?:'.format(prompt)).lower()
        if answer == 'y':
            return True
        elif answer == 'n':
            return False
        else:
            return cls.y_or_n_question(prompt)

    def create_character(self):
        move_choice = []
        excluded_moves = []
        existing = self.y_or_n_question('Existing game?')
        name = input('What is your character\'s name?: ')
        if existing:
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
                print('Could not find character!')
                self.create_character()
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
            self.learn_random_moveset(character, 4, use_input=True)
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
        all_scenes = [scene for scene in self.character.scene.to_scenes.filter(is_locked=False).all()]
        all_scenes.extend([scene for scene in self.character.scene.from_scenes.filter(is_locked=False).all()])
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
                if callback_method == self.take_one_of:
                    menu_item_name = "Take {} ({})"
                elif callback_method == self.use_one_of:
                    menu_item_name = "Use {} ({})"
                else:
                    menu_item_name = "{} ({})"
                # If value is greater than one, append a MenuItem
                result.append(MenuItem(menu_item_name.format(inv_key.split('.')[0],
                                                             len(inv_value)),
                                       callback_method(inv_value, character)))
            elif len(inv_value) == 1:
                # If value is equal to one, append the inventory
                result.append(inv_value[0])
        return result

    def check_inventory(self):
        owned_items = self.compress_inventory_menu(self.character.agent_items.all(),
                                                   self.character,
                                                   self.use_one_of)
        owned_items = [MenuItem('Use {}'.format(item.name), self.use_item(item))
                       if isinstance(item, Inventory)
                       else item for item in owned_items]
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
            item_to_use.method()
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

    def take_item(self, item):
        def wrapper():
            self.character.take_inventory(item)
        return wrapper

    def use_item(self, item):
        def wrapper():
            print('=' * len(item.description.split('\\n')[0]))
            print(re.sub(r'\\n', '\n', item.description))
            print('=' * len(item.description.split('\\n')[0]))
            self.character.use_inventory(item)
        return wrapper

    def find_items(self):
        items = self.compress_inventory_menu([it for it in self.character.scene.scene_items.order_by('id').all()],
                                             self.character,
                                             self.take_one_of)
        if len(items) > 0:
            items.append(MenuItem('Take All Items', self.add_all_items))
        items = [MenuItem('Take {}'.format(item.name), self.take_item(item))
                 if isinstance(item, Inventory) else item for item in items]
        return items

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
            ]
            enemies = self.character.scene.agents.filter(type='EN', hp__gt=0)
            if enemies.count() > 0:
                menu_items.pop(0)
                for enemy in enemies:
                    menu_items.append(MenuItem('Fight {}'.format(enemy.name), self.fight_enemy(self.character, enemy)))
            menu_items.extend(self.find_items())
            print(self.character.scene.complete_description)
            print(self.character.scene.inventory_description)
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
        print('GAME OVER')
        self.character.dies(self.start, self.initiate_flow)

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

    def learn_random_moveset(self, character, move_count, use_input=False):
        move_choice = []
        excluded_moves = []
        while len(move_choice) < move_count:
            moves = Move.objects\
                        .filter(user=None)\
                        .exclude(id__in=excluded_moves)\
                        .all()
            if use_input:
                move = self.menuify_queryset(moves,
                                             'Move:\t\tType:\tEffect:\tUses MP:',
                                             'type',
                                             'effect_magnitude',
                                             'special_move')
            else:
                move = moves.order_by('?').first()
            if move is not None:
                move_choice.append(move)
                excluded_moves.append(move.id)
            else:
                print('Bad choice!')
        for move in move_choice:
            character.learn_move(move)

    def add_enemies(self, num_enemies=5):
        # Clear enemies
        for scene in self.adventure.scenes.all():
            scene.agents.filter(type='EN').all().delete()
        # Add random enemies to random scenes
        for times in range(num_enemies):
            random_enemy = self.random_enemy()
            self.learn_random_moveset(
                self.random_scene().add_enemy(random_enemy),
                2
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
