#!/usr/bin/env python
"""
Check if all migrations are applied correctly.
Run this script before starting the server to ensure database consistency.
"""

import os
import sys
import django
from django.core.management import call_command
from io import StringIO

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_chatbot.settings')
django.setup()

def check_migrations():
    """Check if all migrations are applied correctly."""
    print("Checking migrations...")
    
    # Capture the output of showmigrations command
    output = StringIO()
    call_command('showmigrations', stdout=output)
    migrations_output = output.getvalue()
    
    # Check if there are any unapplied migrations
    if '[X]' in migrations_output and '[ ]' in migrations_output:
        print("\nWarning: There are unapplied migrations. Please run:")
        print("python manage.py migrate\n")
        print("Unapplied migrations:")
        
        for line in migrations_output.split('\n'):
            if '[ ]' in line:
                print(f"  {line.strip()}")
        
        return False
    
    if '[ ]' in migrations_output:
        print("\nWarning: None of the migrations have been applied. Please run:")
        print("python manage.py migrate\n")
        return False
    
    print("All migrations are applied correctly.")
    return True

def check_missing_migrations():
    """Check if there are any missing migrations that need to be created."""
    print("\nChecking for missing migrations...")
    
    # Capture the output of makemigrations --check command
    output = StringIO()
    try:
        call_command('makemigrations', '--check', stdout=output, stderr=output)
        print("No missing migrations detected.")
        return True
    except SystemExit:
        print("\nWarning: There are model changes that require new migrations. Please run:")
        print("python manage.py makemigrations\n")
        return False

if __name__ == "__main__":
    migrations_ok = check_migrations()
    missing_migrations_ok = check_missing_migrations()
    
    if not migrations_ok or not missing_migrations_ok:
        print("\nDatabase is not in sync with models. Please apply the necessary migrations.")
        sys.exit(1)
    
    print("\nDatabase is in sync with models. All good!")
    sys.exit(0)