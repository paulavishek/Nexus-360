from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import getpass
import sys

class Command(BaseCommand):
    help = 'Creates an admin user non-interactively if username doesn\'t exist'

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True, help='Admin username')
        parser.add_argument('--email', required=True, help='Admin email')
        parser.add_argument('--password', help='Admin password (if not provided, will prompt securely)')
        parser.add_argument('--noinput', action='store_true', help='Do not prompt for password')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists'))
            return
        
        # Get password if not provided and not using --noinput
        if not password and not options['noinput']:
            # Prompt for password securely (without echoing to console)
            password = getpass.getpass('Enter password: ')
            password_confirm = getpass.getpass('Confirm password: ')
            
            if password != password_confirm:
                self.stdout.write(self.style.ERROR('Passwords do not match'))
                sys.exit(1)
        
        if not password:
            self.stdout.write(self.style.ERROR('No password provided and --noinput specified'))
            sys.exit(1)
        
        # Create the admin user
        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Admin user "{username}" created successfully'))