from django.utils import timezone
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
            "id",
            "first_name",
            "last_name",
            "city",
            "country",
            "bio",
            "picture",
            "followers",
        )

        read_only_fields = ("id", "followers")


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "user", "content", "created_at")


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("post", "content")


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "post", "content")
        read_only_fields = ("id", "post")


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("content", "picture", "scheduled_time")

    def create(self, validated_data):
        user = self.context["request"].user
        scheduled_time = validated_data.get("scheduled_time")

        post = Post.objects.create(
            user=user,
            content=validated_data.get("content"),
            picture=validated_data.get("picture"),
            scheduled_time=scheduled_time,
            is_published=(scheduled_time is None or scheduled_time <= timezone.now()),
        )

        if scheduled_time and scheduled_time > timezone.now():
            from core.tasks import publish_post

            publish_post.apply_async(args=[post.id], eta=scheduled_time)

        return post


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
