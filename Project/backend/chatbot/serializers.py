from rest_framework import serializers
# 👇 Yahan 'Report' ki jagah 'CommunityReport' karein
from .models import CommunityReport, NewsPost, HealthTip, DengueStat

class ReportSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = CommunityReport  # 👈 Yahan b Change karein
        fields = '__all__'

class NewsPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsPost
        fields = '__all__'

class HealthTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthTip
        fields = '__all__'