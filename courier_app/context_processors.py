from django.conf import settings


def map_settings(request):
    # Map tile providers no longer require API keys (using OpenFreeMap)
    return {}
