from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class PostureSummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    window_start = models.DateTimeField()
    window_end = models.DateTimeField()
    time_in_good_posture = models.IntegerField()
    time_in_bad_posture = models.IntegerField()
    times_notified = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.window_start} to {self.window_end}"