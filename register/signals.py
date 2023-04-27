from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver
@receiver(post_migrate)
def create_initial_admin(sender, **kwargs):
    User = get_user_model()
    if not User.objects.filter(username='admin1').exists():
        User.objects.create_superuser('admin1', 'admin1@example.com', 'admin1', is_admin=True)
