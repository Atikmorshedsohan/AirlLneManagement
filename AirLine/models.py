from django.db import models
from django.contrib.auth.models import User

class Registration(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    nid = models.CharField(max_length=20)
    age = models.PositiveIntegerField()

    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    def __str__(self):
        return self.full_name
