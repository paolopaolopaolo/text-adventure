from django.core.management.base import BaseCommand
from adventure.models import Story, Agent, Inventory, Scene
from game_mechanics.flow import FlowRunner


class Command(BaseCommand):

    help = "Clears the story board of agents and inventory"

    @classmethod
    def choose_story(cls):
        print("Choose story to reset")
        stories = Story.objects.all()
        story_choice = FlowRunner.menuify_queryset(stories,
                                                   'Adventure Name:')
        return story_choice

    def handle(self, *args, **options):
        story = self.choose_story()
        # Remove all enemies and players currently in a scene in a story
        Agent.objects\
             .filter(scene__story=story)\
             .delete()
        # Remove all items from the story
        Inventory.objects.filter(found_location__story=story).delete()
        # Get all locked scenes and unlock them
        locked_scenes = Scene.objects.filter(is_locked=True).all()
        for scene in locked_scenes:
            scene.is_locked = False
            scene.save()
        print("{} cleared of enemies and players! All scenes unlocked.".format(story.name))
