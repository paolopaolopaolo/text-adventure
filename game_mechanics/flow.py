from adventure.models import Agent, Story, Move
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")


class FlowRunner:
    adventure = None
    character = None

    def choose_story(self):
        stories = Story.objects.all()
        story_menu = 'Option:\tAdventure Name:'
        for idx, story in enumerate(stories):
            story_menu = '\n'.join((
                '{}\t{}'.format(idx, story.name),
            ))
        print(story_menu)
        story_choice = stories[input('Choose your adventure (option number): ')]
        self.adventure = story_choice

    def create_character(self):
        move_choice = []
        random_moves = Move.objects.filter(special_move=False).order_by('?')[5]
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
        random_move_menu_header = 'Option:\tAdventure Name:\tType:\tEffect:'
        while len(move_choice) < 3:
            random_move_menu = random_move_menu_header
            for idx, move in enumerate(random_moves):
                random_move_menu = '\n'.join((
                    random_move_menu,
                    '{}\t{}\t{}\t{}'.format(idx, move.name, move.type, move.effect_magnitude),
                ))
            move_to_add = random_moves[input('Choose a move (option number): ')]
            move_choice.append(move_to_add)
            random_moves = random_moves.exclude(id=move_to_add.id)
        for move in move_choice:
            character.learn_move(move)
        self.character = character

    def start(self):
        print(self.adventure.description)
        self.character.scene = self.adventure.first_scene
        self.main_loop()

    def navigate(self):
        scene_keys = []
        scene_destinations = "Option:\tPath to:\t"
        for idx, scene in enumerate(self.character.scene.to_scenes.all()):
            scene_destinations = '\n'.join((
                scene_destinations,
                '{}\t{}'.format(idx, scene.name)
            ))
            scene_keys.append(scene)
        for idx, scene in enumerate(self.character.scene.from_scenes.all()):
            scene_destinations = '\n'.join((
                scene_destinations,
                '{}\t{}'.format(idx + self.character.scene.to_scenes.count(), scene.name)
            ))
            scene_keys.append(scene)
        try:
            scene_to_switch_to = scene_keys[input('Option: ')]
            self.character.scene = scene_to_switch_to
            self.character.save()
        except KeyError:
            pass

    def use_inventory(self):
        pass

    def take_item(self):
        pass

    def main_loop(self):
        menu_items = [
            ('Navigate', self.navigate),
            ('Check Inventory', self.use_inventory),
            ('Take item', self.take_item)
        ]

        while self.character.hp > 0:
            print(self.character.scene.complete_description)
            menu_table = "MENU:\nOption:\tIndex:"
            for idx, item in enumerate(menu_items):
                menu_table = '\n'.join((
                    menu_table,
                    '{}\t{}'.format(idx, item)
                ))
            print(menu_table)
            menu_items[int(input('Option: '))][1]()
        print('GAME OVER')

    def initiate_flow(self):
        self.choose_story()
        print('Story Chosen!')
        self.create_character()
        print('Character created!')
        self.start()

if __name__ == '__main__':
    flow = FlowRunner()
    flow.initiate_flow()