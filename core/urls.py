from django.urls import path, include
from rest_framework import routers

from core.views import PostViewSet, CommentViewSet, ProfileViewSet

app_name = "core"

router = routers.DefaultRouter()
router.register('posts', PostViewSet)
router.register('comments', CommentViewSet)
router.register("profiles", ProfileViewSet)

urlpatterns = [path("", include(router.urls))]
