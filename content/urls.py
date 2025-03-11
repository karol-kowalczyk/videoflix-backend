from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VideoViewSet
from django.conf.urls.static import static
from videoflix_app import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


router = DefaultRouter()
router.register(r'videos', VideoViewSet)

urlpatterns = [
    path('', include(router.urls)),
] + staticfiles_urlpatterns()