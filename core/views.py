from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, generics, mixins, status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from core.models import Profile, Post, Comment
from core.serializers import (
    PostSerializer,
    CommentSerializer,
    ToggleFollowSerializer,
    ProfileListSerializer,
    ProfileRetrieveSerializer,
)


class StandardPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class MyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileRetrieveSerializer

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


class ProfileViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Profile.objects.all()
    serializer_class = ProfileListSerializer
    pagination_class = StandardPagination

    def get_serializer_class(self):
        if self.action == "retrieve":
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


class FollowersListViewSet(ListAPIView):
    serializer_class = ProfileListSerializer

    def get_queryset(self):
        profile = self.request.user.profile
        return Profile.objects.filter(user__in=profile.followers.all())


class FollowedListViewSet(ListAPIView):
    serializer_class = ProfileListSerializer

    def get_queryset(self):
        user = self.request.user
        return Profile.objects.filter(followers=user)


class ToggleFollowView(generics.GenericAPIView):
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
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = StandardPagination


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = StandardPagination
