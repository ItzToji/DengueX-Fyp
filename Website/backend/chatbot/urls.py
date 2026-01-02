from django.urls import path
from .views import (
    # 1. Auth
    signup_api,
    login_api,
    google_login_api, 
    get_security_question,
    reset_password_api,
    change_password_api,
    
    # 2. Profile
    get_profile_api,
    update_profile_api,
    
    # 3. Dashboard & Analytics
    dashboard_stats_api,
    analytics_data_api,
    public_dashboard_stats,
    
    # 4. Chatbot & Reports
    chat_api,
    get_chat_sessions,
    get_chat_messages,
    delete_chat_session,
    submit_report_api,
    get_reports_api,
    identify_mosquito_api,
    
    # 5. ADMIN PANEL & News/Tips
    admin_get_all_reports,
    admin_update_report_status,
    admin_update_stats,
    admin_delete_city,      # ✅ City Delete
    admin_delete_news,      # ✅ News Delete
    admin_delete_tip,       # ✅ Tip Delete
    admin_post_news,        # ✅ Post News
    add_tip,                # ✅ Add Tip
    get_all_users,
    toggle_user_block_status,
    get_news_api,           # Public News List
    get_all_tips            # Public Tips List
)

urlpatterns = [
    # --- Authentication ---
    path('signup/', signup_api, name='signup'),
    path('login/', login_api, name='login'),
    path('google-login/', google_login_api, name='google_login'),
    path('get-security-question/', get_security_question, name='get_security_question'),
    path('reset-password-secure/', reset_password_api, name='reset_password_secure'),
    path('change-password/', change_password_api),

    # --- Profile ---
    path('get-profile/', get_profile_api, name='get_profile'),
    path('update-profile/', update_profile_api, name='update_profile'),

    # --- Dashboard & Public Stats ---
    path('dashboard-data/', dashboard_stats_api, name='dashboard_stats'),
    path('analytics/', analytics_data_api, name='analytics_data'),
    path('public-stats/', public_dashboard_stats),

    # --- Chatbot ---
    path('chat/', chat_api, name='chat_api'),
    path('chat-sessions/', get_chat_sessions, name='chat_sessions'),
    path('chat-messages/<int:session_id>/', get_chat_messages, name='chat_messages'),
    path('delete-chat/<int:session_id>/', delete_chat_session, name='delete_chat_session'),

    # --- Reports & AI ---
    path('submit-report/', submit_report_api, name='submit_report'),
    path('get-reports/', get_reports_api, name='get_reports'),
    path('identify-mosquito/', identify_mosquito_api, name='identify_mosquito'),

    # --- ✅ ADMIN PANEL ROUTES (Fixed) ---
    path('admin/all-reports/', admin_get_all_reports, name='admin_all_reports'),
    path('admin/update-status/', admin_update_report_status, name='admin_update_status'),
    path('admin/users/', get_all_users),
    path('admin/toggle-block-user/', toggle_user_block_status),

    # --- City Management ---
    path('admin/update-stats/', admin_update_stats, name='admin_update_stats'),
    path('admin/delete-city/', admin_delete_city), # 👈 Fixed (No <int:id>)

    # --- News & Broadcast ---
    path('news/', get_news_api, name='news_list'),
    path('admin/post-news/', admin_post_news, name='admin_post_news'),
    path('admin/delete-news/', admin_delete_news), # 👈 Fixed (No <int:id>)

    # --- Health Tips ---
    path('health-tips/', get_all_tips, name='tips_list'),
    path('admin/add-tip/', add_tip, name='add_tip'),
    path('admin/delete-tip/', admin_delete_tip),   # 👈 Fixed (No <int:id>)
]