from django.urls import path, include
from rest_framework import routers

from core.views import PostViewSet, CommentViewSet, ProfileViewSet, MyProfileView

app_name = "core"

router = routers.DefaultRouter()
router.register("posts", PostViewSet)
router.register("comments", CommentViewSet)
router.register("profiles", ProfileViewSet)

urlpatterns = [
    path("profiles/me/", MyProfileView.as_view(), name="me"),
    path("", include(router.urls)),
]
