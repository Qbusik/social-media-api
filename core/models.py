import os
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify


def upload_image(instance, filename):
    return instance.get_image_path(filename)


class Profile(models.Model):
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name="profile"
    )
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=150, blank=True)
    country = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)

    def get_image_path(self, filename):
        _, extension = os.path.splitext(filename)
        filename = f"{slugify(self.user.email)}-{uuid.uuid4()}{extension}"
        return os.path.join("uploads/profile/", filename)

    picture = models.ImageField(blank=True, null=True, upload_to=upload_image)
    followers = models.ManyToManyField(
        get_user_model(), related_name="following", blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

    class Meta:
        ordering = ["-created_at"]


class Post(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.TextField(blank=True)

    def get_image_path(self, filename):
        _, extension = os.path.splitext(filename)
        filename = f"{slugify(self.user.email)}-{uuid.uuid4()}{extension}"
        return os.path.join("uploads/posts/", filename)

    picture = models.ImageField(blank=True, null=True, upload_to=upload_image)
    likes = models.ManyToManyField(
        get_user_model(), related_name="liked_posts", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    scheduled_time = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return f"Post by: {self.user.email}"

    class Meta:
        ordering = ["-created_at"]


class Comment(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by: {self.user.email}"

    class Meta:
        ordering = ["-created_at"]
