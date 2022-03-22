from django.dispatch import receiver 
from django.db.models.signals import post_save 

from social_distribution.models import Author, Inbox


@receiver(post_save, sender=Author)
def create_inbox(sender, instance, created, **kwargs):
    '''
    Upon Author creation, create an Inbox for this new user.
    '''
    if created:
        Inbox.objects.create(author=instance)
