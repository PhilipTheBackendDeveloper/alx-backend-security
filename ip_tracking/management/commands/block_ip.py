from django.core.management.base import BaseCommand
from ip_tracking.models import BlockedIP

class Command(BaseCommand):
    help = 'Add an IP address to the blacklist'

    def add_arguments(self, parser):
        parser.add_argument('--ip', type=str, required=True, help='IP address to block')

    def handle(self, *args, **kwargs):
        ip = kwargs['ip']

        obj, created = BlockedIP.objects.get_or_create(ip_address=ip)

        if created:
            self.stdout.write(self.style.SUCCESS(f"IP {ip} has been blocked."))
        else:
            self.stdout.write(self.style.WARNING(f"IP {ip} is already blocked."))
