from django.urls import reverse
from rest_framework import status

from core.models import Post, Comment, Profile


class TestComment:
    def test_add_and_remove_comment(self, auth_client, sample_user, another_user):
        profile_to_follow = Profile.objects.create(user=another_user)
        post = Post.objects.create(user=another_user)
        profile_to_follow.followers.add(sample_user)

        user_comment = Comment.objects.create(
            post=post, user=sample_user, content="test_comment"
        )
        another_user_comment = Comment.objects.create(
            post=post, user=another_user, content="test_comment"
        )

        res = auth_client.get(reverse("core:posts-detail", kwargs={"pk": post.pk}))

        assert res.status_code == status.HTTP_200_OK
        assert res.data["comments"][0]["content"] == "test_comment"

        res = auth_client.delete(
            reverse("core:comments-detail", kwargs={"pk": user_comment.pk})
        )

        assert res.status_code == status.HTTP_204_NO_CONTENT
        assert not Comment.objects.filter(pk=user_comment.pk).exists()

        res = auth_client.delete(
            reverse("core:comments-detail", kwargs={"pk": another_user_comment.pk})
        )

        assert res.status_code == status.HTTP_403_FORBIDDEN
        assert Comment.objects.filter(pk=another_user_comment.pk).exists()
