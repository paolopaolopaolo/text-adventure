from adventure.models import Agent, Story, Move
import os


class MenuItem:

    def __init__(self, *args):
        self.name, self.method = args


class FlowRunner:

    def __init__(self):
        self.adventure = None
        self.character = None

    def choose_story(self):
        stories = Story.objects.all()
        story_choice = self.menu_ify_queryset(stories,
                                              'Adventure Name:')
        if story_choice:
            self.adventure = story_choice
        else:
            self.choose_story()

    def create_character(self):
        move_choice = []
        excluded_moves = []
        name = input('What is your character\'s name?: ')
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
            move = self.menu_ify_queryset(
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
        self.character.scene = self.adventure.first_scene
        self.main_loop()

    @classmethod
    def menu_ify_queryset(cls, queryset, header_value, *args, use_header=True):
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
        choice = input('Option: ')
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
        choice = self.menu_ify_queryset(
            (self.character.scene.to_scenes.all() |
             self.character.scene.from_scenes.all()),
            'Path to:'
        )
        if choice:
            self.character.scene = choice
            self.character.save()

    def use_inventory(self):
        pass

    def take_item(self):
        pass

    def main_loop(self):
        menu_items = [
            MenuItem('Navigate', self.navigate),
            MenuItem('Check Inventory', self.use_inventory),
            MenuItem('Take item', self.take_item)
        ]

        while self.character.hp > 0:
            print(self.character.scene.complete_description)
            choice = self.menu_ify_queryset(
                menu_items,
                'Actions:'
            )
            if choice:
                choice.method()
                os.system('clear')
        print('GAME OVER')

    def initiate_flow(self):
        self.choose_story()
        os.system('clear')
        self.create_character()
        os.system('clear')
        self.start()

if __name__ == '__main__':
    flow = FlowRunner()
    flow.initiate_flow()
