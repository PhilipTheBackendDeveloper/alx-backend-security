# ip_tracking/tasks.py
from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from django.db.models import Count
from .models import RequestLog, SuspiciousIP, BlockedIP

@shared_task
def detect_suspicious_ips():
    """
    Runs hourly. Flags IPs:
      - >100 requests in last 1 hour
      - or accessing sensitive paths (/admin, /login, /wp-login, etc) frequently
    When flagged, creates SuspiciousIP and optionally adds to BlockedIP (commented).
    """
    now = timezone.now()
    one_hour_ago = now - timedelta(hours=1)

    # 1) IPs with > 100 requests in the last hour
    ip_counts = (RequestLog.objects
                 .filter(timestamp__gte=one_hour_ago)
                 .values("ip_address")
                 .annotate(req_count=Count("id"))
                 .filter(req_count__gt=100))

    flagged = []
    for rec in ip_counts:
        ip = rec["ip_address"]
        reason = f"{rec['req_count']} requests in last hour"
        SuspiciousIP.objects.update_or_create(ip_address=ip, defaults={"reason": reason, "active": True})
        flagged.append((ip, reason))

    # 2) IPs frequently hitting sensitive endpoints in the last hour
    sensitive_paths = ["/admin", "/login", "/wp-login.php", "/administrator"]
    sensitive_hits = (RequestLog.objects
                      .filter(timestamp__gte=one_hour_ago, path__in=sensitive_paths)
                      .values("ip_address")
                      .annotate(s_hits=Count("id"))
                      .filter(s_hits__gte=10))  # threshold

    for rec in sensitive_hits:
        ip = rec["ip_address"]
        reason = f"{rec['s_hits']} hits to sensitive paths in last hour"
        SuspiciousIP.objects.update_or_create(ip_address=ip, defaults={"reason": reason, "active": True})
        flagged.append((ip, reason))

    # Optional: block automatically if extremely abusive
    # for ip, reason in flagged:
    #     BlockedIP.objects.get_or_create(ip_address=ip, defaults={"reason": reason})

    return {"flagged_count": len(flagged)}
