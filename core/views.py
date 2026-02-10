from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from core.models import Profile, Post, Comment
from core.serializers import ProfileSerializer, PostSerializer, CommentSerializer


class StandardPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
