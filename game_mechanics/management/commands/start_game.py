from game_mechanics.flow import FlowRunner
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Runs the Text Adventure Game'

    def handle(self, *args, **options):
        flow = FlowRunner()
        flow.initiate_flow()
