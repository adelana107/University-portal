# portal/management/commands/import_states_lgas.py
import csv
from django.core.management.base import BaseCommand
from portal.models import State, Lga  # Make sure these match your actual model names

class Command(BaseCommand):
    help = 'Import states and LGAs from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            # Skip header if exists
            next(csv_reader, None)
            
            for row in csv_reader:
                state_name = row[0]  # Assuming state is in first column
                lga_name = row[1]    # Assuming LGA is in second column
                
                # Get or create the state
                state, _ = State.objects.get_or_create(name=state_name)
                
                # Create the LGA with the correct field name: state_of_origin instead of state
                Lga.objects.get_or_create(name=lga_name, state_of_origin=state)
                
        self.stdout.write(self.style.SUCCESS('Successfully imported states and LGAs'))