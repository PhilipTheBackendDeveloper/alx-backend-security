from django.db import models
from django.db import models
from django.utils import timezone
class BlockedIP(models.Model):
    """IP addresses that should be blocked immediately."""
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.CharField(max_length=255, blank=True, null=True)
    blocked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address} ({self.reason or 'blocked'})"


class RequestLog(models.Model):
    """Log incoming requests with geolocation info."""
    ip_address = models.GenericIPAddressField()
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    timestamp = models.DateTimeField(default=timezone.now)
    user_agent = models.TextField(blank=True, null=True)

    # Geolocation
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6,
                                   blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6,
                                    blank=True, null=True)

    def __str__(self):
        return f"{self.ip_address} - {self.path} @ {self.timestamp}"


class SuspiciousIP(models.Model):
    """Flagged IPs by the anomaly detection task."""
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.CharField(max_length=500)
    flagged_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.ip_address} - {self.reason}"

