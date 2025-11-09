import datetime
from django.utils.timezone import now # pyright: ignore[reportMissingModuleSource]
from ip_tracking.models import RequestLog
from django.utils.deprecation import MiddlewareMixin # pyright: ignore[reportMissingModuleSource]

class IPTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = request.META.get("HTTP_X_FORWARDED_FOR")
        if ip:
            ip = ip.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")

        RequestLog.objects.create(
            ip_address=ip,
            path=request.path,
            timestamp=now()
        )
