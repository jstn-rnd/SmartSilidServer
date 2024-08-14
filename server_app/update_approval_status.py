from django.core.management.base import BaseCommand
from django.utils import timezone
from server_app.models import Schedule

class Command(BaseCommand):
    help = 'Update RFID approval statuses based on current time'

    def handle(self, *args, **options):
        current_time = timezone.localtime().time()
        schedules = Schedule.objects.all()
        for schedule in schedules:
            schedule.update_rfids_approval(current_time)
        self.stdout.write(self.style.SUCCESS('Successfully updated RFID approvals'))