import tempfile
import pytest
from PIL import Image
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.fixture
def temp_media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    return tmp_path


def create_test_image():
    image = Image.new("RGB", (10, 10))
    tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg")
    image.save(tmp_file, format="JPEG")
    tmp_file.seek(0)
    return tmp_file


@pytest.fixture
def sample_user(db):
    return get_user_model().objects.create_user(
        email="test@test.com", password="password123"
    )


@pytest.fixture
def another_user(db):
    return get_user_model().objects.create_user(
        email="test2@test2.com", password="password123"
    )


@pytest.fixture
def not_followed_user(db):
    return get_user_model().objects.create_user(
        email="test3@test3.com", password="password123"
    )


@pytest.fixture
def auth_client(sample_user):
    client = APIClient()
    client.force_authenticate(sample_user)
    return client
