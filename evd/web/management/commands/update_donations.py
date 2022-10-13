from django.core.management.base import BaseCommand, CommandError
from web.models import Donation,User
from evd import settings
import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        donations = Donation.objects.all()

        venkat = User.objects.get(id=1)

        prev_fin_date = datetime.datetime(day=31, month=3, year=2014)

        for donation in donations:
            if not donation.user:
                donation.user = venkat

            donation.payment_mode = "neft"

            if donation.id <= 96:

                donation.donation_time = prev_fin_date

            if donation.donation_type == "Adopt Digital Classrom":
                donation.donation_type = "Adopt Digital Classroom"

            if donation.donation_type == "Adopt Digital Classroom" and donation.num_centers:
                donation.num_classrooms = donation.num_centers
                donation.num_centers = ""

            donation.save()
