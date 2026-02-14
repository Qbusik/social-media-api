import os

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status

from core.models import Post, Profile
from core.tests.conftest import create_test_image


@pytest.mark.django_db
class TestPost:
    def test_upload_post_image(self, sample_user, temp_media_root):
        tmp_file = create_test_image()

        post = Post.objects.create(
            user=sample_user,
            picture=SimpleUploadedFile(
                name="test.jpg",
                content=tmp_file.read(),
                content_type="image/jpeg",
            ),
        )

        assert "uploads/posts/" in post.picture.name
        assert post.picture.name.endswith(".jpg")
        assert os.path.exists(post.picture.path)

    def test_like_post(
        self,
        auth_client,
        sample_user,
        another_user,
    ):
        post = Post.objects.create(user=sample_user)

        res = auth_client.post(reverse("core:toggle-like", kwargs={"pk": post.pk}))

        assert res.status_code == status.HTTP_200_OK
        assert post.likes.count() == 1

        res = auth_client.post(reverse("core:toggle-like", kwargs={"pk": post.pk}))

        assert res.status_code == status.HTTP_200_OK
        assert post.likes.count() == 0

    def test_view_only_own_and_followed_users_posts(
        self, auth_client, sample_user, another_user, not_followed_user
    ):
        profile_to_follow = Profile.objects.create(user=another_user)
        Profile.objects.create(user=sample_user)
        Profile.objects.create(user=not_followed_user)

        sample_user.following.add(profile_to_follow)

        Post.objects.create(user=not_followed_user)
        Post.objects.create(user=sample_user)
        Post.objects.create(user=another_user)

        res = auth_client.get(reverse("core:posts-list"))

        assert res.status_code == status.HTTP_200_OK
        assert res.data["count"] == 2
