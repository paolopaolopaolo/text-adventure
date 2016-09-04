from django.core.management.base import BaseCommand
from adventure.models import Story, Inventory
from game_mechanics.flow import FlowRunner


class Command(BaseCommand):
    help = 'Adds inventory items to the scenes'

    def generate_random_scene(self, story):
        return story.scenes.order_by('?').first()

    def generate_random_item(self):
        return Inventory.objects\
                        .filter(owner=None, found_location=None, inventory_type='CNS')\
                        .order_by('?')\
                        .first()

    def choose_story(self):
        stories = Story.objects.all()
        story_choice = FlowRunner.menuify_queryset(stories,
                                                   'Adventure Name:')
        return story_choice

    def add_arguments(self, parser):
        parser.add_argument('num_items', nargs='+', type=int)

    def handle(self, *args, **options):
        items = options['num_items'][0]
        story = self.choose_story()
        for idx in range(0, items):
            self.generate_random_scene(story)\
                .add_inventory(self.generate_random_item())
        print("Seeded {} items in Story:{}!".format(items, story.name))
