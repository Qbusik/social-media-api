from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, generics, mixins, status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from core.models import Profile, Post, Comment
from core.permissions import IsOwner
from core.serializers import (
    CommentSerializer,
    ToggleFollowSerializer,
    ProfileListSerializer,
    ProfileRetrieveSerializer,
    PostListSerializer,
    PostRetrieveSerializer,
    PostCreateSerializer,
    ToggleLikeSerializer,
    CommentCreateSerializer,
    CommentUpdateSerializer,
)


class StandardPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class MyProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update user's profile.
    """

    serializer_class = ProfileRetrieveSerializer

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


class ProfileViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """
    List and retrieve user profiles with optional filtering by name and city.
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileListSerializer
    pagination_class = StandardPagination

    def get_permissions(self):
        if self.action in ["destroy", "update", "partial_update"]:
            return [IsOwner()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return ProfileRetrieveSerializer
        return ProfileListSerializer

    def get_queryset(self):
        name = self.request.query_params.get("name")
        city = self.request.query_params.get("city")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(
                Q(first_name__icontains=name) | Q(last_name__icontains=name)
            )

        if city:
            queryset = queryset.filter(city__icontains=city)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter profiles by first or last name contains (ex. ?name=Jacob)",
            ),
            OpenApiParameter(
                "city",
                type=OpenApiTypes.STR,
                description="Filter profiles by city contains (ex. ?name=Warsaw)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FollowersListView(ListAPIView):
    """
    List profiles of users who follow the user.
    """

    serializer_class = ProfileListSerializer

    def get_queryset(self):
        profile = self.request.user.profile
        return Profile.objects.filter(user__in=profile.followers.all())


class FollowedListView(ListAPIView):
    """
    List profiles of users who are followed by the user.
    """

    serializer_class = ProfileListSerializer

    def get_queryset(self):
        user = self.request.user
        return Profile.objects.filter(followers=user)


class ToggleFollowView(generics.GenericAPIView):
    """
    Toggle follow or unfollow for a given user profile.
    """

    serializer_class = ToggleFollowSerializer

    def post(self, request, pk):
        try:
            profile_to_follow = Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            return Response(
                {"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        user = request.user

        if user in profile_to_follow.followers.all():
            profile_to_follow.followers.remove(user)
            followed = False
        else:
            profile_to_follow.followers.add(user)
            followed = True

        profile_to_follow.save()
        serializer = self.get_serializer(profile_to_follow)

        return Response(
            {"followed": followed, "profile": serializer.data},
            status=status.HTTP_200_OK,
        )


class PostViewSet(viewsets.ModelViewSet):
    """
    Manage own posts and list posts from user and followed users.
    """

    queryset = Post.objects.all()
    serializer_class = PostListSerializer
    pagination_class = StandardPagination

    def get_permissions(self):
        if self.action in ["destroy", "update", "partial_update"]:
            return [IsOwner()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PostRetrieveSerializer
        if self.action == "create":
            return PostCreateSerializer
        return PostListSerializer

    def get_queryset(self):
        user = self.request.user
        followed_ids = user.following.values_list("user_id", flat=True)

        queryset = Post.objects.filter(
            Q(user=user) | Q(user__id__in=followed_ids), is_published=True
        )

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(user__profile__first_name__icontains=search)
                | Q(user__profile__last_name__icontains=search)
            )

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "search",
                type=OpenApiTypes.STR,
                description="Filter profiles by first or last name contains (ex. ?name=Jacob)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ToggleLikeView(generics.GenericAPIView):
    """
    Toggle like or unlike for a given post.
    """

    serializer_class = ToggleLikeSerializer

    def post(self, request, pk):
        try:
            post_to_like = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

        user = request.user

        if user in post_to_like.likes.all():
            post_to_like.likes.remove(user)
            like = False
        else:
            post_to_like.likes.add(user)
            like = True

        post_to_like.save()
        serializer = self.get_serializer(post_to_like)

        return Response(
            {"liked": like, "profile": serializer.data},
            status=status.HTTP_200_OK,
        )


class LikedPostsView(ListAPIView):
    """
    List posts liked by the user.
    """

    serializer_class = PostListSerializer

    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(likes=user)


class CommentViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Create, update, and delete own comments on posts.
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action in ["destroy", "update", "partial_update"]:
            return [IsOwner()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ("update", "partial_update"):
            return CommentUpdateSerializer
        if self.action == "create":
            return CommentCreateSerializer
        return CommentSerializer

    def create(self, request, *args, **kwargs):
        post_id = request.data.get("post")
        if not post_id:
            return Response(
                {"detail": "Post ID is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, post=post)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
