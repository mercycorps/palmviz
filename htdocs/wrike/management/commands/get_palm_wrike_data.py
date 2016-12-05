from django.core.management.base import BaseCommand, CommandError

from wrike import utils

class Command(BaseCommand):
    """
    Usage: python manage.py get_palm_wrike_data
    """
    help = 'Fetches PALM Wrike data under "PALM Support" folder'

    def add_arguments(self, parser):
        #parser.add_argument("-u", "--username", type=str, required=True)
        #parser.add_argument('--read_ids', nargs='*', type=int)
        pass

    def handle(self, *args, **options):
        if utils.process_wrike_data() == False:
            #send out an email
            pass