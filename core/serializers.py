from rest_framework import serializers

from core.models import Profile, Post, Comment


class ProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("first_name", "last_name", "city", "country", "picture")


class ProfileRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("first_name", "last_name", "city", "country", "bio", "picture", "followers")


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class ToggleFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "followers")
