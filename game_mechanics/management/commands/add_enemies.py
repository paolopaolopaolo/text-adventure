from django.core.management.base import BaseCommand
from adventure.models import Story, Agent, Move
from game_mechanics.flow import FlowRunner


class Command(BaseCommand):
    help = 'Adds enemies to the scenes'

    def choose_story(self):
        stories = Story.objects.all()
        story_choice = FlowRunner.menuify_queryset(stories,
                                                   'Adventure Name:')
        return story_choice

    def choose_scene(self, story):
        scenes = story.scenes.all()
        scene_choice = FlowRunner.menuify_queryset(scenes,
                                                   'Scene:')
        return scene_choice

    def choose_enemy(self):
        enemies = Agent.objects.filter(scene=None, type='EN')
        enemy_choice = FlowRunner.menuify_queryset(enemies,
                                                   'Enemy Make:')
        return enemy_choice

    def choose_moveset(self, character):
        move_choice = []
        excluded_moves = []
        random = input('Randomize moveset (y/n)?').lower()
        if random == 'y':
            random = True
        else:
            random = False
        while len(move_choice) < 2:
            moves = Move.objects\
                        .filter(user=None, special_move=False)\
                        .exclude(id__in=excluded_moves)\
                        .all()
            if not random:
                move = FlowRunner.menuify_queryset(moves,
                                                   'Move Name:\tType:\tEffect:',
                                                   'type',
                                                   'effect_magnitude')
            else:
                move = moves.order_by('?').first()
            if move:
                move_choice.append(move)
                excluded_moves.append(move.id)

        for move in move_choice:
            character.learn_move(move)

    def handle(self, *args, **options):
        story = self.choose_story()
        scene = self.choose_scene(story)
        enemy = self.choose_enemy()
        scene.add_enemy(enemy)
        self.choose_moveset(enemy)
        print("{}(enemy) planted in {} of {}".format(enemy.name, scene.name, story.name))