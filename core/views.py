from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, generics, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from core.models import Profile, Post, Comment
from core.serializers import ProfileSerializer, PostSerializer, CommentSerializer


class StandardPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class MyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


class ProfileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    pagination_class = StandardPagination

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


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = StandardPagination


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = StandardPagination
