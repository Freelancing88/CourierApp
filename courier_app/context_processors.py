from django.conf import settings

def map_settings(request):
    return {
        'MAPBOX_ACCESS_TOKEN': getattr(settings, 'MAPBOX_ACCESS_TOKEN', ''),
        'MAPTILER_API_KEY': getattr(settings, 'MAPTILER_API_KEY', ''),
        'STADIA_API_KEY': getattr(settings, 'STADIA_API_KEY', ''),
        'CUSTOM_MAP_TILE_URL': getattr(settings, 'CUSTOM_MAP_TILE_URL', ''),
    }
