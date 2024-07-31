from django.core.management.base import BaseCommand
from usermodel.models import User
from django.utils import timezone
import os
from datetime import timedelta


class Command(BaseCommand):
    help = """Analyzes user free trial. 
            If expired set free trial to False.
            """

    def handle(self, *args, **options):
        # Your command logic here
        self.stdout.write(self.style.SUCCESS(f"{timezone.now()} - Checking free trial"))

        # get all the users
        users = User.objects.filter(has_threads=True)

        # get the free trial days
        free_trial_days = int(os.environ["FREE_TRIAL_DAYS"])

        for usr in users:
            print(f"User {usr.username}")
            # check if not paid
            if usr.is_paid:
                continue
            # check if the date joined is more than free trial days in the past
            if usr.date_joined + timedelta(days=free_trial_days) < timezone.now():
                print("free trial expired")
                # udpate the user and set the free trial to expired
                usr.is_free_trial = False
                usr.save()
            else:
                # make sure that the free trial flag is True
                usr.is_free_trial = True
                usr.save()
