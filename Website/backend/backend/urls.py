from django.contrib import admin
from django.urls import path, include
from django.conf import settings             # 👈 Import 1
from django.conf.urls.static import static   # 👈 Import 2

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chatbot.urls')),
]

# 👇 YE HISSA SABSE ZAROORI HAI (Images serve karne ke liye)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)