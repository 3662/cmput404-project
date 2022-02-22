from django.db import models

class Author(models.Model):
    display_name = models.CharField(max_length=20, primary_key=True, blank=False,\
         default=None, unique=True)

    slug = models.SlugField(blank=False, unique=True) # url friendly string
    type = models.CharField(max_length=20, default="author")
    id = models.IntegerField()
    url = models.URLField()
    host = models.URLField()
    github = models.URLField()
    profile_image = models.URLField()

    def __str__(self):
        return self.display_name