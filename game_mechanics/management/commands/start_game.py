from game_mechanics.flow import FlowRunner
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        flow = FlowRunner()
        flow.initiate_flow()
