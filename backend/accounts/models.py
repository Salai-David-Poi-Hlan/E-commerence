from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    email=models.EmailField(unique=True)


    def save(self,*args,**kwargs):
        self.email=self.email.strip().lower()
        super().save(*args,**kwargs)


        