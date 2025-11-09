# ip_tracking/management/commands/block_ip.py
from django.core.management.base import BaseCommand, CommandError
from ip_tracking.models import BlockedIP

class Command(BaseCommand):
    help = "Add an IP to the block list: python manage.py block_ip 1.2.3.4 'reason'"

    def add_arguments(self, parser):
        parser.add_argument("ip", type=str)
        parser.add_argument("--reason", type=str, default="manual block")

    def handle(self, *args, **options):
        ip = options["ip"]
        reason = options["reason"]
        obj, created = BlockedIP.objects.get_or_create(ip_address=ip, defaults={"reason": reason})
        if created:
            self.stdout.write(self.style.SUCCESS(f"Blocked IP {ip}"))
        else:
            raise CommandError(f"IP {ip} is already blocked.")
