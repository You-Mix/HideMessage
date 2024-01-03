from django.db import models

# Create your models here.
class EncodedMessage(models.Model):
    encoded_image = models.ImageField(upload_to='encoded_images/')
    decoding_key = models.CharField(max_length=255)