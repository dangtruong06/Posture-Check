from rest_framework import serializers
from .models import PostureSummary

class PostureSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostureSummary
        fields = ['id', 'user', 'window_start', 'window_end', 'time_in_good_posture', 'time_in_bad_posture', 'times_notified']