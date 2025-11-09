from django.db import models

class RequestLog(models.Model):
    ip_address = models.CharField(max_length=45)  # supports IPv4 + IPv6
    path = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address} - {self.path} - {self.timestamp}"
