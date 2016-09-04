from adventure.models import Agent, Story, Move, Inventory
import os
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
        if Agent.objects.filter(name=name).count() > 0:
            continue_game = input('Continue Game (y/n)?: ').lower()
            if continue_game == 'y':
                print('Confirm which character you\'re loading.')
                self.character = self.menuify_queryset(
                    Agent.objects.filter(name=name).all(),
                    'Agent:\tDescription:',
                    'description'
                )
        else:
            description = input('Tell us about this character: ')
            character = Agent(type='PNR',
                              name=name,
                              description=description,
                              hp=100,
                              mp=10,
                              attack_dmg=0,
                              spc_attack_dmg=0)
            character.save()
            choice_num = 5

            while len(move_choice) < 3:
                random_moves = Move.objects\
                                   .filter(user=None, special_move=False)\
                                   .exclude(id__in=excluded_moves)\
                                   .order_by('?')[:choice_num]
                move = self.menuify_queryset(
                    random_moves,
                    'Move Name:\tType:\tEffect:',
                    'type',
                    'effect_magnitude'
                )
                if move:
                    move_choice.append(move)
                    excluded_moves.append(move.id)
                    choice_num -= 1
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
                return chosen_item
            except IndexError:
                print('No option')
        return

    def navigate(self):
        choice = self.menuify_queryset(
            (self.character.scene.to_scenes.all() |
             self.character.scene.from_scenes.all()),
            'Path to:'
        )
        if choice is not None:
            self.character.scene = choice
            self.character.save()
        os.system('clear')

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

    def check_inventory(self):
        owned_items = self.character.agent_items.all()
        if owned_items.count() == 0:
            print('++++++++++++++++++++++++')
            print('You have no items')
            print('++++++++++++++++++++++++')
            return
        self.character.show_inventory()
        item_to_use = self.menuify_queryset(owned_items,
                                            'Item:')
        if item_to_use is not None:
            print('='*20)
            print(item_to_use.description)
            self.character.use_inventory(item_to_use)
            self.check_inventory()
        else:
            return

    def find_items(self):
        if self.character.scene.scene_items.count() == 0:
            print('++++++++++++++++++++++++')
            print('There are no items here.')
            print('++++++++++++++++++++++++')
            return
        print(self.character.scene.inventory_description())
        item = self.menuify_queryset(self.character.scene.scene_items.order_by('id').all(),
                                     'Item:')
        if item is not None:
            self.character.take_inventory(item)
            os.system('clear')

    def fight_enemy(self, player, enemy):
        def combat_loop():
            actors = [enemy, player]
            random.shuffle(actors)
            current_actor_idx = 0
            while player.hp > 0 and enemy.hp > 0:
                # Current actor uses move
                current_actor = actors[current_actor_idx]
                if current_actor.type == 'EN':
                    move = random.choice(current_actor.moves.all())
                    if move.effect_magnitude < 0:
                        effect = current_actor.use_move(player, move)
                        print("{} uses {}!".format(current_actor.name, move.name))
                        print("Your {} stat is decreases by {}!".format(move.type, effect))
                    else:
                        effect = current_actor.use_move(enemy, move)
                        print("{} uses {}!".format(current_actor.name, move.name))
                        print("{}'s {} stat increases by {}!".format(enemy.name, move.type, move.effect_magnitude))
                else:
                    potential_moves = [move for move in player.moves.all()]
                    potential_items = [item for item in player.agent_items.all()]
                    potential_moves.extend(potential_items)
                    move = self.menuify_queryset(potential_moves,
                                                 "Move/Item:")
                    if isinstance(move, Move):
                        if move.effect_magnitude < 0:
                            effect = current_actor.use_move(enemy, move)
                            print("{} uses {}!".format(current_actor.name, move.name))
                            print("{}'s {} stat is decreases by {}!".format(enemy.name,
                                                                            move.type,
                                                                            effect))
                        else:
                            effect = current_actor.use_move(current_actor, move)
                            print("{} uses {}!".format(current_actor.name, move.name))
                            print("Your {} stat increases by {}!".format(move.type,
                                                                         effect))
                    if isinstance(move, Inventory):
                        current_actor.use_inventory(move)

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
                MenuItem('Check Inventory', self.check_inventory),
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
                os.system('clear')
                choice.method()
        self.character.delete()
        print('GAME OVER')
        print('Play again(y/n)?')
        again = input('').lower()
        if again == 'y':
            self.initiate_flow()

    def initiate_flow(self):
        try:
            self.choose_story()
            os.system('clear')
            self.create_character()
            os.system('clear')
            self.start()
        except KeyboardInterrupt:
            self.initiate_flow()

if __name__ == '__main__':
    flow = FlowRunner()
    flow.initiate_flow()
