from core.models import Post

from celery import shared_task


@shared_task
def publish_post(post_id):
    try:
        post = Post.objects.get(id=post_id)
        post.is_published = True
        post.scheduled_time = None
        post.save()
    except Post.DoesNotExist:
        pass
