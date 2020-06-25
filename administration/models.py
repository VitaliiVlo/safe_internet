from django.db import models


class Website(models.Model):
    domain = models.URLField(unique=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class BlockRequest(models.Model):
    website = models.ForeignKey(Website, related_name='block_requests', on_delete=models.CASCADE)
    description = models.TextField()
    email = models.EmailField()
    ip = models.GenericIPAddressField()
    is_accepted = models.BooleanField(null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
