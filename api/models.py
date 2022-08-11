from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=255, unique=True)
    details = models.CharField(max_length=255)

    def __str__(self):
        return str(self.id) + '->' + str(self.name)
