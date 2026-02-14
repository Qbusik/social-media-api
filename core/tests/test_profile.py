import os

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status

from core.models import Profile
from core.tests.conftest import create_test_image


@pytest.mark.django_db
class TestProfile:
    def test_upload_profile_image(self, sample_user, temp_media_root):
        tmp_file = create_test_image()

        profile = Profile.objects.create(
            user=sample_user,
            picture=SimpleUploadedFile(
                name="test.jpg",
                content=tmp_file.read(),
                content_type="image/jpeg",
            ),
        )

        assert "uploads/profile/" in profile.picture.name
        assert profile.picture.name.endswith(".jpg")
        assert os.path.exists(profile.picture.path)

    def test_follow_profile(
        self,
        auth_client,
        sample_user,
        another_user,
    ):
        Profile.objects.create(user=sample_user)
        profile_to_follow = Profile.objects.create(user=another_user)

        res = auth_client.post(
            reverse("core:toggle-follow", kwargs={"pk": profile_to_follow.pk})
        )

        assert res.status_code == status.HTTP_200_OK
        assert profile_to_follow.followers.count() == 1
        assert sample_user.following.count() == 1

        res = auth_client.post(
            reverse("core:toggle-follow", kwargs={"pk": profile_to_follow.pk})
        )

        assert res.status_code == status.HTTP_200_OK
        assert profile_to_follow.followers.count() == 0
        assert sample_user.following.count() == 0

    def test_me_endpoint(self, auth_client, sample_user):
        Profile.objects.create(user=sample_user, first_name="test123")
        res = auth_client.get(reverse("core:profile-me"))

        assert res.status_code == status.HTTP_200_OK
        assert res.data["first_name"] == "test123"
