from django.db import models
from django.contrib.postgres.fields import ArrayField

# user model, created when new user begins to use application
# updated when user creates additional playlists

class User(models.Model):
    user_name = models.CharField(primary_key=True, max_length=200)
    join_date = models.DateTimeField('date joined')
    playlists = ArrayField(models.CharField(max_length=200), default=list)
