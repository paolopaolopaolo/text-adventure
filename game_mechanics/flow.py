from adventure.models import Agent, Story, Move


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

    def go_command(self):

    def main_loop(self):
        menu_items = {
            '0': ''
        }
        while self.character.hp > 0:
            print(self.character.scene.complete_description)
            for idx, item in

            input('doot')
        print('GAME OVER')

    def initiate_flow(self):
        self.choose_story()
        print('Story Chosen!')
        self.create_character()
        print('Character created!')
        self.start()