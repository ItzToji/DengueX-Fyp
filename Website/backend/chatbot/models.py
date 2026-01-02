from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    security_question = models.CharField(max_length=255)
    security_answer = models.CharField(max_length=255)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    is_vaccinated = models.CharField(max_length=20, default="No") # Yes/No
    recent_test_date = models.CharField(max_length=50, blank=True, null=True) # Date stored as string for simplicity

    def __str__(self):
        return self.user.username
class CommunityReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='reports/', blank=True, null=True)
    description = models.TextField()
    
    # ✅ New Field Added
    area_name = models.CharField(max_length=255, blank=True, null=True) 
    
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    ai_result = models.CharField(max_length=200, default="Pending Analysis")
    confidence = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.user.username} in {self.area_name}"
       
from django.db import models

class DengueStat(models.Model):
    city_name = models.CharField(max_length=100, unique=True)
    active_cases = models.IntegerField(default=0)
    recovered = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    
    # ✅ Location Fields (Map ke liye zaroori)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # ✅ Last Updated Time (Chart ke liye zaroori)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.city_name

# ✅ Chat Session (Jo Sidebar mein dikhega: "Dengue Symptoms", "Prevention", etc.)
class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# ✅ Chat Messages (Jo us session ke andar hongay)
class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    sender = models.CharField(max_length=10) # 'user' or 'bot'
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sender}: {self.text[:20]}"     

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True) # Chat ka Topic
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    role = models.CharField(max_length=50) # 'user' or 'assistant'
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:20]}..."    

class NewsUpdate(models.Model):
    title = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.city}: {self.title}"    
# Create your models here.
class NewsPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    city = models.CharField(max_length=100, default="All Pakistan")  # 👈 New Field
    date_posted = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} ({self.city})"
# ✅ ADD THIS TOO (IF YOU WANT HEALTH TIPS SEPARATE)
class HealthTip(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title