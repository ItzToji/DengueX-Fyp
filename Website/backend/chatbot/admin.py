from django.contrib import admin
from .models import UserProfile, DengueStat, HealthTip, NewsUpdate

# 1. User Profile & News
admin.site.register(UserProfile)
admin.site.register(NewsUpdate)

# 2. Dengue Stats (Detailed View)
@admin.register(DengueStat)
class DengueStatAdmin(admin.ModelAdmin):
    list_display = ('city_name', 'active_cases', 'recovered', 'deaths', 'last_updated')

# 3. ✅ Health Tips (PreventionTip ki jagah ye lagayen)
@admin.register(HealthTip)
class HealthTipAdmin(admin.ModelAdmin):
    # HealthTip model mein 'icon_class' nahi hai, 'date_posted' hai
    list_display = ('title', 'date_posted')