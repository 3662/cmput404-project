from django.db import models
from django.dispatch import receiver 
from django.db.models.signals import post_save 
from django.contrib.auth.hashers import make_password


class ServerNode(models.Model):

    class Meta:
        verbose_name = 'ServerNode'

    host = models.CharField(max_length=500, null=False)
    username = models.CharField(max_length=100, null=False)
    password = models.CharField(max_length=128, null=False)

    def __str__(self):
        return self.host
    


@receiver(post_save, sender=ServerNode)
def hash_password(sender, instance, created, **kwargs):
    '''
    Upon ServerNode creation, hash the plain password and save it. 
    '''
    if created:
        # instance.password = make_password(instance.password)
        instance.save()
