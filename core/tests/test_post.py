import os
import time
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
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

        res = auth_client.get(reverse("core:liked"))

        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 1

        res = auth_client.post(reverse("core:toggle-like", kwargs={"pk": post.pk}))

        assert res.status_code == status.HTTP_200_OK
        assert post.likes.count() == 0

        res = auth_client.get(reverse("core:liked"))

        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 0

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

    def test_scheduled_post_mock(self, auth_client, sample_user):
        post_data = {
            "content": "Test",
            "scheduled_time": (timezone.now() + timedelta(seconds=3)).isoformat(),
        }

        with patch("core.tasks.publish_post.apply_async") as mock_task:
            res = auth_client.post(
                reverse("core:posts-list"), data=post_data, format="json"
            )
            assert res.status_code == 201

            post = Post.objects.filter(user=sample_user).latest("created_at")
            post_id = post.id

            assert post.is_published is False

            mock_task.assert_called_once()
            call_args, call_kwargs = mock_task.call_args

            assert call_kwargs.get("args") == [post_id]

            eta = call_kwargs.get("eta")
            assert eta is not None
            assert abs((eta - post.scheduled_time).total_seconds()) < 1
