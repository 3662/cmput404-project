from django.db import models
from django.contrib.auth.hashers import make_password


class ServerNodeManager(models.Manager):

    def create(self, username, password, host):
        '''
        Creates a new ServerNode.
        '''
        node = self.model(username=username, password=make_password(password), host=host)
        node.save()
        return node
        
