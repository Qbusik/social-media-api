from rest_framework import serializers

from core.models import Profile, Post, Comment


class ProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("first_name", "last_name", "city", "country", "picture")


class ProfileRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "first_name",
            "last_name",
            "city",
            "country",
            "bio",
            "picture",
            "followers",
        )


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("user", "content", "created_at")


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("post", "content")


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "content", "picture")


class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "user", "content")


class PostRetrieveSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ("id", "user", "content", "picture", "comments")


class ToggleFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "followers")


class ToggleLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "likes")
