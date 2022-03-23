from django.db import models


class ServerNode(models.Model):

    class Meta:
        verbose_name = 'ServerNode'

    host = models.URLField(null=False)
    username = models.CharField(max_length=100, null=False)
    password = models.CharField(max_length=128, null=False)

    