from django.urls import path, include
from rest_framework import routers

from core.views import (
    PostViewSet,
    CommentViewSet,
    ProfileViewSet,
    MyProfileView,
    ToggleFollowView,
    FollowersListView,
    FollowedListView,
)

app_name = "core"

router = routers.DefaultRouter()
router.register("posts", PostViewSet, basename="posts")
router.register("comments", CommentViewSet, basename="comments")
router.register("profiles", ProfileViewSet, basename="profiles")


urlpatterns = [
    path("profiles/me/", MyProfileView.as_view(), name="profile-me"),
    path(
        "profiles/toggle-follow/<int:pk>/",
        ToggleFollowView.as_view(),
        name="toggle-follow",
    ),
    path(
        "profiles/followers/",
        FollowersListView.as_view(),
        name="followers",
    ),
    path(
        "profiles/followed/",
        FollowedListView.as_view(),
        name="followed",
    ),
    path("", include(router.urls)),
]
