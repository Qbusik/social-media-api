from core.models import Post

from celery import shared_task


@shared_task
def count_posts():
    return Post.objects.count()
