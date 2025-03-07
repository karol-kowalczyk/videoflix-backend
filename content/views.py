from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.core.cache.backends.base import DEFAULT_TIMEOUT 
from django.conf import settings

# Use CACHETTL from settings or fall back to the default timeout
CACHE_TTL = getattr(settings, 'CACHETTL', DEFAULT_TIMEOUT)

@cache_page(CACHE_TTL)
def recipes_view(request):
    return render(request, 'cookbook/recipes.html', {
        'recipes': get_recipes()
    })
