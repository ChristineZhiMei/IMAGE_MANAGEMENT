from django.db import models

class photoIndex(models.Model):
    class Meta:
        app_label = 'photos'
    date = models.DateField()
    thumbnailPath = models.CharField(max_length=255)
    filePath = models.CharField(max_length=255,unique=True)
    createTime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.date)
