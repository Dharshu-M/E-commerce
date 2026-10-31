from django.db import models


class Registration(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    user_name = models.CharField(max_length=15)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    