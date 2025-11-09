# ip_tracking/middleware.py
import json
import logging
import requests
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden

from .models import BlockedIP, RequestLog

logger = logging.getLogger(__name__)

GEO_CACHE_PREFIX = "ipgeo:"
GEO_CACHE_TTL = getattr(settings, "IP_GEOLOCATION_CACHE_TTL", 60 * 60 * 24)  # 24 hours


class IPBlockMiddleware:
    """
    Middleware that:
      - Blocks requests from IPs present in BlockedIP model (returns 403)
      - Logs each request to RequestLog
      - Looks up geolocation (cached for 24h)
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Optionally set a preferred geolocation service (settings.IP_GEO_SERVICE)
        self.geo_service = getattr(settings, "IP_GEO_SERVICE", "ipapi")  # 'ipapi' fallback

    def __call__(self, request):
        # Get client IP (basic method). In production behind proxies, use django-ipware or X-Forwarded-For parsing.
        ip = self.get_client_ip(request)

        # Check blocklist
        if BlockedIP.objects.filter(ip_address=ip).exists():
            logger.warning(f"Blocked request from {ip}")
            return HttpResponseForbidden("Your IP has been blocked.")

        # Geolocation (cached)
        geo = self.get_geo_info(ip)

        # Log the request (non-blocking)
        try:
            RequestLog.objects.create(
                ip_address=ip,
                path=request.path,
                method=request.method,
                timestamp=timezone.now(),
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000],
                country=geo.get("country_name"),
                city=geo.get("city"),
                latitude=geo.get("latitude"),
                longitude=geo.get("longitude"),
            )
        except Exception as e:
            logger.exception("Failed to write RequestLog: %s", e)

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Basic IP extraction. If behind proxy, ensure correct header is used."""
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            # X-Forwarded-For may contain a list: client,proxy1,proxy2
            ip = xff.split(",")[0].strip()
            return ip
        return request.META.get("REMOTE_ADDR")

    def get_geo_info(self, ip):
        """Return a dict with country_name, city, latitude, longitude. Use cache."""
        cache_key = f"{GEO_CACHE_PREFIX}{ip}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        geo = {"country_name": None, "city": None, "latitude": None, "longitude": None}

        # Primary: try django-ipgeolocation if configured (we try a generic approach)
        # Fallback: use ipapi.co public API (no API key required for basic info)

        try:
            if self.geo_service == "ipapi":
                url = f"https://ipapi.co/{ip}/json/"
                resp = requests.get(url, timeout=3)
                if resp.status_code == 200:
                    data = resp.json()
                    geo["country_name"] = data.get("country_name")
                    geo["city"] = data.get("city")
                    # ipapi returns latitude/longitude as floats or strings
                    lat = data.get("latitude") or data.get("lat")
                    lon = data.get("longitude") or data.get("lon")
                    if lat:
                        try:
                            geo["latitude"] = float(lat)
                        except Exception:
                            geo["latitude"] = None
                    if lon:
                        try:
                            geo["longitude"] = float(lon)
                        except Exception:
                            geo["longitude"] = None
            else:
                # If django-ipgeolocation package or other configured provider is present,
                # you can implement provider-specific lookup here. We keep fallback simple.
                pass
        except Exception as e:
            logger.debug("Geo lookup failed for %s: %s", ip, e)

        cache.set(cache_key, geo, GEO_CACHE_TTL)
        return geo
