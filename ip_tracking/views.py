# ip_tracking/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt

from ratelimit.core import is_ratelimited
from ratelimit.exceptions import Ratelimited
from django.utils.decorators import method_decorator
from django.views import View


def rate_limit_check(request):
    """
    Return (allowed: bool, reason: str).
    Authenticated users: 10 requests/min by IP.
    Anonymous users: 5 requests/min by IP.
    Uses django-ratelimit core helper is_ratelimited (programmatic).
    """
    if request.user and request.user.is_authenticated:
        rate = "10/m"
    else:
        rate = "5/m"

    # is_ratelimited(..., increment=True) will increase the counter
    limited = is_ratelimited(request, key="ip", rate=rate, method=["POST", "GET", "PUT", "DELETE"], increment=True)
    return (not limited, f"rate limit exceeded ({rate})" if limited else "")


@csrf_exempt
def login_view(request):
    """
    Example login view (POST) that uses programmatic rate limiting.
    On rate limit hit, returns 429.
    """
    allowed, reason = rate_limit_check(request)
    if not allowed:
        return JsonResponse({"detail": reason}, status=429)

    if request.method != "POST":
        return JsonResponse({"detail": "method not allowed"}, status=405)

    username = request.POST.get("username")
    password = request.POST.get("password")
    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        return JsonResponse({"detail": "logged in"}, status=200)
    return JsonResponse({"detail": "invalid credentials"}, status=401)

# You can use the same pattern for other sensitive endpoints like password reset, profile update, etc.
