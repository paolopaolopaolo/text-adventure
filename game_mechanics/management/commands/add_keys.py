from django.core.management.base import BaseCommand
from adventure.models import Story, Inventory, Scene
from game_mechanics.flow import FlowRunner


class Command(BaseCommand):
    help = 'Adds key inventory items to scenes'

    def generate_random_scene(self, story, excluded_scenes):
        bad_ids = [scene.id for scene in excluded_scenes]
        return story.scenes.exclude(id__in=bad_ids).order_by('?').first()

    def generate_random_key_item(self):
        return Inventory.objects\
                        .filter(owner=None, found_location=None, inventory_type='KI')\
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
            print("KEY ADDITION")
            print("Choose a scene to find this object:")
            scene = FlowRunner.menuify_queryset(Scene.objects.filter(story=story).all(),
                                                "Scene:")
            print("Choose a Key Item object:")
            key_item_kwargs = {
                "found_location": None,
                "owner": None,
                "inventory_type": "KI",
            }
            key_item = FlowRunner.menuify_queryset(Inventory.objects.filter(**key_item_kwargs).all(),
                                                   "Key Item:")
            scene.add_inventory(key_item)
            print("Choose a scene to lock with this object:")
            lock_scene = FlowRunner.menuify_queryset(
                Scene.objects.filter(story=story).exclude(id=scene.id).all(),
                "Scene:"
            )
            lock_scene.is_locked = True
            lock_scene.unlocking_item = scene.scene_items.filter(name=key_item.name).first()
            lock_scene.save()
        print("Saved key items!")
