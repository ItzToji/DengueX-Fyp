import re
import uuid
import random
import json
from datetime import datetime, timedelta
from PIL import Image
import google.generativeai as genai
import requests

# Django Core Imports
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import render
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate

# REST Framework Imports
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

# Models Imports (Duplicate names removed)
from .models import (
    UserProfile, 
    DengueStat, 
    HealthTip, 
    ChatSession, 
    ChatMessage, 
    NewsUpdate,
    CommunityReport,
    NewsPost, 
    HealthTip
)

# Serializers
from .serializers import ReportSerializer
# ==========================================
# 0. CONFIGURATION (AI SETTINGS)
# ==========================================
LONGCAT_API_KEY = "ak_1yY8HL0rz9oG86o5Ru5Wj9r01mQ3H" 
# Agar ye URL kaam na kare to '/openai/v1' hata kar check karein
API_URL = "https://api.longcat.chat/openai/v1/chat/completions" 
MODEL_NAME = "LongCat-Flash-Chat"
SYSTEM_INSTRUCTION = "You are DengueX Assistant. Answer strictly about Dengue fever, symptoms, and prevention."
GOOGLE_API_KEY = "AIzaSyAnnwi2t2qZf5M-E-pFC8xMTVN6GVsWDSM" 

genai.configure(api_key=GOOGLE_API_KEY)

# ==========================================
# 1. AUTHENTICATION APIs
# ==========================================

@api_view(["POST"])
@permission_classes([AllowAny])
def signup_api(request):
    username = request.data.get("username")
    password = request.data.get("password")
    
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username is already taken."}, status=400)

    try:
        user = User.objects.create_user(username=username, password=password)
        UserProfile.objects.create(user=user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"message": "Account created!", "token": token.key, "username": user.username})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_api(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "message": "Login successful", 
            "username": user.username,
            "token": token.key,
            "is_admin": user.is_staff  # ✅ YE HAI WO LINE JO MISSING THI
        })
    else:
        return Response({"error": "Invalid username or password"}, status=401)
    
    
@api_view(['POST'])
@permission_classes([AllowAny])
def get_security_question(request):
    username = request.data.get('username')
    try:
        user = User.objects.get(username=username)
        # Profile se question nikalein
        # (Make sure UserProfile model mein 'security_question' field ho)
        if hasattr(user, 'userprofile') and user.userprofile.security_question:
            return Response({"question": user.userprofile.security_question})
        else:
            return Response({"error": "No security question set."}, status=400)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

@api_view(["POST"])
@permission_classes([AllowAny])
def google_login_api(request):
    """
    Google Login API
    """
    email = request.data.get("email")
    name = request.data.get("name")
    
    if not email:
        return Response({"error": "Email is required"}, status=400)

    # 1. Check if user already exists
    user = User.objects.filter(username=email).first()
    
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"message": "Login Successful", "username": user.username, "token": token.key})
    
    # 2. If user does not exist, Create New Account
    try:
        random_password = str(uuid.uuid4()) 
        user = User.objects.create_user(username=email, email=email, password=random_password)
        UserProfile.objects.create(
            user=user, 
            full_name=name, 
            security_question="Google Login", 
            security_answer="Google"
        )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"message": "Account Created", "username": user.username, "token": token.key})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


# ==========================================
# 2. PASSWORD RESET APIs
# ==========================================

@api_view(["POST"])
@permission_classes([AllowAny])
def get_security_question(request):
    username = request.data.get("username")
    try:
        user = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)
        return Response({"question": profile.security_question})
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    except UserProfile.DoesNotExist:
        return Response({"error": "Profile not found"}, status=404)
    
@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_api(request):
    # 👇 DEBUG: Print exactly what React sent to the terminal
    print("📢 INCOMING DATA:", request.data) 

    username = request.data.get("username")
    new_password = request.data.get("new_password")
    
    # 👇 FLEXIBLE FIX: Check for 'security_answer' OR 'answer'
    answer = request.data.get("security_answer") or request.data.get("answer")

    # 1. Validation
    if not username or not answer or not new_password:
        # This is the error you were getting
        print(f"❌ MISSING FIELDS! Got User: {username}, Answer: {answer}, Pass: {new_password}")
        return Response({"error": "All fields are required."}, status=400)

    try:
        user = User.objects.get(username=username)
        
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Response({"error": "This account does not have security questions."}, status=400)

        # 2. Check Answer
        if profile.security_answer.strip().lower() == answer.strip().lower():
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password reset successful!"})
        else:
            return Response({"error": "Incorrect security answer."}, status=400)

    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=404)
    except Exception as e:
        print(f"❌ SERVER ERROR: {str(e)}")
        return Response({"error": str(e)}, status=500)

# ==========================================
# 3. PROFILE APIs
# ==========================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_profile_api(request):
    try:
        user = request.user
        profile = UserProfile.objects.get(user=user)
        return Response({
            "username": user.username,
            "full_name": profile.full_name or "",
            "age": profile.age or "",
            "blood_group": profile.blood_group or "",
            "is_vaccinated": profile.is_vaccinated or "No",
            "recent_test_date": profile.recent_test_date or ""
        })
    except UserProfile.DoesNotExist:
        return Response({"error": "Profile not found"}, status=404)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_profile_api(request):
    try:
        user = request.user
        profile = UserProfile.objects.get(user=user)

        profile.full_name = request.data.get("full_name", profile.full_name)
        if request.data.get("age"): profile.age = int(request.data.get("age"))
        profile.blood_group = request.data.get("blood_group", profile.blood_group)
        profile.is_vaccinated = request.data.get("is_vaccinated", profile.is_vaccinated)
        profile.recent_test_date = request.data.get("recent_test_date", profile.recent_test_date)
        
        profile.save()
        return Response({"message": "Profile updated successfully!"})
        
    except UserProfile.DoesNotExist:
        return Response({"error": "Profile not found"}, status=404)

# ==========================================
# 4. CHATBOT APIs (DEBUG MODE ENABLED)
# ==========================================

@api_view(["POST"])
@permission_classes([AllowAny])
def signup_api(request):
    username = request.data.get("username")
    password = request.data.get("password")
    
    # 1. Capture the new fields
    sec_q = request.data.get("security_question")
    sec_a = request.data.get("security_answer")

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username is already taken."}, status=400)

    try:
        # 2. Create User (create_user automatically hashes the password)
        user = User.objects.create_user(username=username, password=password)
        
        # 3. Create Profile with the security data
        UserProfile.objects.create(
            user=user,
            security_question=sec_q,
            security_answer=sec_a
        )
        
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            "message": "Account created!", 
            "token": token.key, 
            "username": user.username
        })
        
    except Exception as e:
        # It's good practice to log 'e' here for the developer, 
        # but be careful sending raw exceptions to the frontend in production.
        return Response({"error": "Something went wrong. Please try again."}, status=500)
@api_view(["POST"])
@permission_classes([AllowAny])
def login_api(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        
        # ✅ Check Role based on is_staff (Admin) status
        is_admin = user.is_staff 
        role = "admin" if is_admin else "user"

        return Response({
            "message": "Login successful", 
            "username": user.username,
            "token": token.key,
            "is_admin": is_admin,  # Frontend ke liye Boolean (true/false)
            "role": role           # Frontend ke liye String ('admin'/'user')
        })
    else:
        return Response({"error": "Invalid username or password"}, status=401)
    
    
    
@api_view(["POST"])
@permission_classes([AllowAny])
def google_login_api(request):
    email = request.data.get("email")
    name = request.data.get("name")
    if not email: return Response({"error": "Email is required"}, status=400)
    user = User.objects.filter(username=email).first()
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"message": "Login Successful", "username": user.username, "token": token.key})
    try:
        random_password = str(uuid.uuid4()) 
        user = User.objects.create_user(username=email, email=email, password=random_password)
        UserProfile.objects.create(user=user, full_name=name, security_question="Google", security_answer="Google")
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"message": "Account Created", "username": user.username, "token": token.key})
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(["POST"])
@permission_classes([AllowAny])
def get_security_question(request):
    username = request.data.get("username")
    try:
        user = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)
        return Response({"question": profile.security_question})
    except: return Response({"error": "User not found"}, status=404)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_profile_api(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        return Response({
            "username": request.user.username,
            "full_name": profile.full_name,
            "age": profile.age,
            "blood_group": profile.blood_group,
            "is_vaccinated": profile.is_vaccinated,
            "recent_test_date": profile.recent_test_date
        })
    except: return Response({"error": "Profile not found"}, status=404)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_profile_api(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        profile.full_name = request.data.get("full_name", profile.full_name)
        if request.data.get("age"): profile.age = int(request.data.get("age"))
        profile.blood_group = request.data.get("blood_group", profile.blood_group)
        profile.is_vaccinated = request.data.get("is_vaccinated", profile.is_vaccinated)
        profile.recent_test_date = request.data.get("recent_test_date", profile.recent_test_date)
        profile.save()
        return Response({"message": "Updated!"})
    except: return Response({"error": "Error updating"}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_sessions(request):
    sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
    data = [{"id": s.id, "title": s.title} for s in sessions]
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_messages(request, session_id):
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
        messages = session.messages.all().order_by('timestamp')
        
        data = []
        for m in messages:
            sender_name = 'bot' if m.role == 'assistant' else 'user'
            data.append({"sender": sender_name, "text": m.content})
            
        return Response(data)
    except ChatSession.DoesNotExist:
        return Response({"error": "Chat not found"}, status=404)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_chat_session(request, session_id):
    try:
        # Fetch the session only if it belongs to the logged-in user
        session = ChatSession.objects.get(id=session_id, user=request.user)
        session.delete()
        return Response({"message": "Chat session deleted successfully."}, status=200)
    except ChatSession.DoesNotExist:
        return Response({"error": "Chat session not found or access denied."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_api(request):
    try:
        user = request.user
        user_message = request.data.get('message') 
        session_id = request.data.get('session_id')

        if not user_message:
            return Response({"response": "Please type a message."})

        session = None
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=user)
            except ChatSession.DoesNotExist: pass 
        
        if not session:
            title = " ".join(user_message.split()[:4]) + "..."
            session = ChatSession.objects.create(user=user, title=title)
        
        ChatMessage.objects.create(session=session, role='user', content=user_message)

        bot_response = "I am DengueX AI."
        try:
            headers = {"Authorization": f"Bearer {LONGCAT_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": MODEL_NAME,
                "messages": [{"role": "system", "content": SYSTEM_INSTRUCTION}, {"role": "user", "content": user_message}],
                "temperature": 0.7
            }
            res = requests.post(API_URL, json=payload, headers=headers, timeout=20)
            if res.status_code == 200:
                data = res.json()
                if 'choices' in data: bot_response = data['choices'][0]['message']['content']
            else:
                bot_response = f"AI Error: {res.status_code}"
        except Exception as e:
            bot_response = f"Connection Error: {str(e)}"

        ChatMessage.objects.create(session=session, role='assistant', content=bot_response)

        return Response({"response": bot_response, "session_id": session.id, "title": session.title})

    except Exception as e:
        print(e)
        return Response({"response": "Server Error"}, status=200)

# ==========================================
# 5. DASHBOARD APIs
# ==========================================

# ... Baki imports ...

@api_view(['GET'])
@permission_classes([AllowAny])
def dashboard_stats_api(request):
    try:
        # 1. Calculate Aggregate Stats
        stats = DengueStat.objects.aggregate(
            total_cases=Sum('active_cases') + Sum('recovered') + Sum('deaths'),
            active=Sum('active_cases'),
            recovered=Sum('recovered'),
            deaths=Sum('deaths')
        )

        # 2. Get All City Stats (For Map & Table)
        city_stats = DengueStat.objects.all()
        city_data = [
            {
                "id": stat.id,
                "city": stat.city_name,
                "active": stat.active_cases,
                "recovered": stat.recovered,
                "deaths": stat.deaths,
                "latitude": stat.latitude,
                "longitude": stat.longitude
            } 
            for stat in city_stats
        ]

        # 3. Get Recent Health Tips (ERROR YAHAN THA - FIXED)
        # Humne 'icon_class' hata diya kyunki HealthTip model mein ye nahi hai.
        tips = HealthTip.objects.all().order_by('-date_posted')[:5]
        tips_data = [
            {
                "id": t.id, 
                "title": t.title, 
                "description": t.description,
                "date": t.date_posted.strftime("%Y-%m-%d") if t.date_posted else ""
            } 
            for t in tips
        ]

        # 4. Final Response Structure
        return Response({
            "summary": {
                "total_reports": stats['total_cases'] or 0,
                "active": stats['active'] or 0,
                "recovered": stats['recovered'] or 0,
                "deaths": stats['deaths'] or 0
            },
            "stats": city_data,  # Map aur Cards ke liye
            "city_stats": city_data, # Backward compatibility ke liye
            "health_tips": tips_data
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)

# ✅ 2. DELETE TIP (POST Method Use Karein)
@api_view(['POST'])  # 👈 Ye Line Sabse Zaroori Hai
@permission_classes([IsAdminUser])
def admin_delete_tip(request):
    try:
        tip_id = request.data.get('id')
        
        if not tip_id:
            return Response({"error": "Tip ID is required"}, status=400)
            
        deleted, _ = HealthTip.objects.filter(id=tip_id).delete()
        
        if deleted:
            return Response({"message": "Tip deleted successfully!"})
        else:
            return Response({"error": "Tip not found"}, status=404)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
# ✅ 2. DELETE HEALTH TIP

@api_view(["GET"])
@permission_classes([AllowAny])
def analytics_data_api(request):
    try:
        # 1. Sabse pehle Admin ka Total Active Cases nikalein
        # (Kyunki yehi Official Data hai jo aapne add kiya hai)
        total_active_admin = DengueStat.objects.aggregate(Sum('active_cases'))['active_cases__sum'] or 0

        # 2. Chart Data Generate karein
        chart_data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=29) # Pichle 30 din
        
        # Din count karein
        delta = (end_date - start_date).days + 1

        for i in range(delta):
            date_obj = start_date + timedelta(days=i)
            display_date = date_obj.strftime("%b %d") # e.g. "Dec 23"
            
            # --- LOGIC ---
            # Hum chahte hain ke graph "Aaj" ke din WOHI dikhaye jo aapne add kiya hai.
            # Aur pichle dino mein thoda kam dikhaye taake "Trend" banta hua nazar aaye.
            
            days_from_today = (end_date.date() - date_obj.date()).days # 0 means Aaj, 1 means Kal...
            
            if days_from_today == 0:
                # Aaj ka data = Total Admin Active Cases
                estimated = total_active_admin
            else:
                # Pichle dino ka data fake generate karein (Thoda kam)
                # Har din peeche jane par 5% kam karte jayen
                decrease_amount = int(total_active_admin * 0.05 * days_from_today) 
                # Ya simple minus logic: (days * 10)
                
                estimated = max(0, total_active_admin - decrease_amount)

            chart_data.append({
                "date": display_date,
                "cases": estimated
            })
            
        return Response(chart_data)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
@api_view(["GET"])
@permission_classes([AllowAny])
def get_news_api(request):
    news_list = NewsUpdate.objects.all().order_by('-date')
    data = [{"id": n.id, "title": n.title, "city": n.city, "content": n.content, "date": n.date.strftime("%d %b, %Y")} for n in news_list]
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_report_api(request):
    try:
        # Frontend se data lein
        desc = request.data.get('description')
        lat = request.data.get('latitude')
        lng = request.data.get('longitude')
        area = request.data.get('area_name')  # 👈 Area Name Receive Kia
        image = request.FILES.get('image')

        # Database me Save karein
        report = CommunityReport.objects.create(
            user=request.user,
            description=desc,
            latitude=lat,
            longitude=lng,
            area_name=area,  # 👈 Yahan Save ho raha hai
            image=image
        )

        # AI Mock Logic (Optional)
        report.ai_result = "Dengue Larva Detected 🦟"
        report.confidence = 88
        report.save()

        return Response({"message": "Report Submitted Successfully!", "id": report.id})

    except Exception as e:
        return Response({"error": str(e)}, status=500)   

@api_view(['POST'])
@permission_classes([IsAdminUser])  # Sirf Admin hi ye kar sake
def toggle_user_block_status(request):
    try:
        user_id = request.data.get('user_id')
        user = User.objects.get(id=user_id)
        
        # Admin khud ko block na kar sake
        if user.is_superuser:
            return Response({"error": "Cannot block Super Admin"}, status=400)

        # Status Toggle (Agar True hai to False, False hai to True)
        user.is_active = not user.is_active
        user.save()
        
        status_msg = "Unblocked" if user.is_active else "Blocked"
        return Response({"message": f"User {status_msg} successfully", "is_active": user.is_active})

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def identify_mosquito_api(request):
    import google.generativeai as genai
    from PIL import Image
    import json

    # 🔑 APNI KEY YAHAN PASTE KAREIN
    GOOGLE_API_KEY = "AIzaSyA5LEWF6G5xWC_iK6wwQZ52X3-hFnxxVvs" 
    genai.configure(api_key=GOOGLE_API_KEY)

    try:
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({"error": "No image uploaded"}, status=400)

        img = Image.open(image_file)

        # ✅ FIX: Aapki list se 'gemini-2.5-flash' uthaya hai
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
        except:
            # Agar direct naam na chale to 'models/' ke sath try karein
            model = genai.GenerativeModel('models/gemini-2.5-flash')

        print("🤖 Using Model: gemini-2.5-flash")

        prompt = """
        You are an expert entomologist. Analyze this image strictly.
        
        1. FIRST, determine if the image contains a mosquito.
           - If it is a bear, cat, car, human, or random object, output JSON: {"is_mosquito": false}
           
        2. IF it IS a mosquito, identify it and output JSON:
           {
             "is_mosquito": true,
             "species": "Exact Species Name",
             "risk": "High/Medium/Low",
             "details": "Visual features",
             "habitat": "Breeding grounds",
             "confidence": 95
           }
           
        Output ONLY valid JSON. Do not include markdown formatting like ```json.
        """

        response = model.generate_content([prompt, img])
        result_text = response.text.strip()
        
        # JSON Safai
        cleaned_text = result_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned_text)

        # ✅ LOGIC: Agar Machar nahi hai
        if data.get("is_mosquito") == False:
            return Response({
                "species": "Not a Mosquito 🚫",
                "risk": "N/A",
                "details": "This does not look like a mosquito. Please upload a clear insect photo.",
                "habitat": "N/A",
                "confidence": 0
            })

        # ✅ LOGIC: Agar Machar hai
        return Response({
            "species": data.get("species", "Unknown Mosquito"),
            "risk": data.get("risk", "Unknown"),
            "details": data.get("details", "No details available"),
            "habitat": data.get("habitat", "Unknown"),
            "confidence": data.get("confidence", 85)
        })

    except Exception as e:
        print(f"AI Critical Error: {str(e)}")
        return Response({"error": f"AI Error: {str(e)}"}, status=500)@api_view(['GET'])
# 2. Function ko update karein
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # ✅ YE LINE BOHT ZAROORI HAI
def get_reports_api(request):
    try:
        # Ab hum sure hain ke user logged in hai
        reports = CommunityReport.objects.filter(user=request.user).order_by('-created_at')
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)
    except Exception as e:
        print(f"Error fetching reports: {e}")
        return Response({"error": "Something went wrong"}, status=500)

# ==========================================
# 6. ADMIN DASHBOARD APIs (Only for Superusers)
# ==========================================

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_get_all_reports(request):
    """Admin ko sari reports dikhane ke liye"""
    reports = CommunityReport.objects.all().order_by('-created_at')
    data = [{
        "id": r.id,
        "username": r.user.username, # User ka naam
        "description": r.description,
        "location": f"{r.latitude}, {r.longitude}",
        "ai_result": r.ai_result, # Isay hum Status ke tor par use karenge
        "image": r.image.url if r.image else None,
        "date": r.created_at.strftime("%d %b, %I:%M %p")
    } for r in reports]
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_update_report_status(request):
    """Report ka status change karne ke liye (e.g., Pending -> Resolved)"""
    report_id = request.data.get('id')
    new_status = request.data.get('status') # e.g., "Resolved ✅" or "Fake Report ❌"
    
    try:
        report = CommunityReport.objects.get(id=report_id)
        report.ai_result = new_status # Hum ai_result field ko hi update kar rahe hain taake migration na karni pare
        report.save()
        return Response({"message": "Report status updated!"})
    except CommunityReport.DoesNotExist:
        return Response({"error": "Report not found"}, status=404)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_update_stats(request):
    try:
        # Raw Data
        raw_city = request.data.get('city_name')
        
        if not raw_city:
            return Response({"error": "City Name is required"}, status=400)

        # ✨ MAGIC FIX: Naam ko Standardize karein (e.g., "multan " -> "Multan")
        city_name = raw_city.strip().title()

        active = request.data.get('active_cases')
        recovered = request.data.get('recovered')
        deaths = request.data.get('deaths')
        lat = request.data.get('latitude')
        lon = request.data.get('longitude')

        defaults_data = {
            'active_cases': int(active) if active else 0,
            'recovered': int(recovered) if recovered else 0,
            'deaths': int(deaths) if deaths else 0
        }

        # Location tab hi update karein agar user ne di ho
        if lat and lon:
            defaults_data['latitude'] = float(lat)
            defaults_data['longitude'] = float(lon)

        # update_or_create ab "Multan" dhoonde ga, chahe user ne "multan" likha ho
        obj, created = DengueStat.objects.update_or_create(
            city_name=city_name, 
            defaults=defaults_data
        )

        return Response({"message": f"{'Created' if created else 'Updated'} {city_name} successfully!"})

    except Exception as e:
        return Response({"error": str(e)}, status=500)

# ✅ 2. DELETE CITY API (NEW)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_delete_city(request):
    try:
        city_id = request.data.get('id')
        if not city_id:
            return Response({"error": "ID required"}, status=400)
            
        DengueStat.objects.filter(id=city_id).delete()
        
        return Response({"message": "City deleted successfully!"})
    except Exception as e:
        
        return Response({"error": str(e)}, status=500)
from django.shortcuts import get_object_or_404
from .models import NewsPost, NewsUpdate  # 👈 Make sure dono imported hain

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .models import NewsPost, NewsUpdate  # Dono models import kar lein

@api_view(['POST'])  # 👈 Sirf POST hona chahiye
@permission_classes([IsAdminUser])
def admin_delete_news(request):
    try:
        news_id = request.data.get('id')
        print(f"🗑️ Delete Request received for ID: {news_id}")

        if not news_id:
            return Response({"error": "News ID is required"}, status=400)
            
        # Pehle NewsPost (Standard) check karein
        deleted, _ = NewsPost.objects.filter(id=news_id).delete()
        
        # Agar wahan nahi mila, to NewsUpdate (Backup) check karein
        if not deleted:
            deleted, _ = NewsUpdate.objects.filter(id=news_id).delete()
        
        if deleted:
            return Response({"message": "News deleted successfully!"})
        else:
            return Response({"error": "News not found"}, status=404)

    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_delete_tip(request):
    try:
        tip_id = request.data.get('id')
        if not tip_id:
            return Response({"error": "Tip ID is required"}, status=400)
            
        deleted, _ = HealthTip.objects.filter(id=tip_id).delete()
        
        if deleted:
            return Response({"message": "Tip deleted successfully!"})
        else:
            return Response({"error": "Tip not found"}, status=404)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_post_news(request):
    """Admin nayi News laga sake"""
    title = request.data.get('title')
    content = request.data.get('content')
    city = request.data.get('city', 'All Pakistan')
    
    NewsUpdate.objects.create(
        title=title,
        content=content,
        city=city,
        date=datetime.now()
    )
    return Response({"message": "News posted successfully!"})
   
@api_view(['GET'])
@permission_classes([IsAdminUser]) 
def get_all_users(request):
    users = User.objects.all().order_by('-date_joined') 
    data = []
    
    for u in users:
        role = "Admin" if u.is_staff else "User"
        data.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": role,
            "date_joined": u.date_joined.strftime("%Y-%m-%d"), 
            "is_active": u.is_active
        })
        
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def post_news(request):
    try:
        NewsPost.objects.create(
            title=request.data.get('title'),
            content=request.data.get('content'),
            city=request.data.get('city', 'All Pakistan')  # 👈 City Save Karein
        )
        return Response({"message": "News Posted Successfully!"})
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_news(request):
    news = NewsPost.objects.all().order_by('-date_posted')
    data = []
    for n in news:
        data.append({
            "id": n.id,
            "title": n.title,
            "content": n.content,
            "city": n.city,  # 👈 Frontend ko City bhejein
            "date": n.date_posted.strftime("%Y-%m-%d")
        })
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_tip(request):
    try:
        HealthTip.objects.create(
            title=request.data.get('title'),
            description=request.data.get('description')
        )
        return Response({"message": "Tip Added!"})
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_tips(request):
    tips = HealthTip.objects.all().order_by('-date_posted')
    data = [{"id": t.id, "title": t.title, "description": t.description} for t in tips]
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_api(request):
    try:
        user = request.user
        new_password = request.data.get('new_password')
        
        if not new_password or len(new_password) < 6:
            return Response({"error": "Password must be at least 6 characters"}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully!"})
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
    
@api_view(['POST'])
@permission_classes([IsAdminUser])
def update_dengue_stats(request):
    try:
        city_name = request.data.get('city_name')
        
        # Data receive karein
        active = request.data.get('active_cases')
        recovered = request.data.get('recovered')
        deaths = request.data.get('deaths')
        lat = request.data.get('latitude')
        lon = request.data.get('longitude')

        if not city_name:
            return Response({"error": "City Name Required"}, status=400)

        # Record update ya create karein
        stat, created = DengueStat.objects.get_or_create(city_name=city_name)
        
        stat.active_cases = int(active) if active else 0
        stat.recovered = int(recovered) if recovered else 0
        stat.deaths = int(deaths) if deaths else 0
        
        # Agar Admin ne Location bheji hai, to save karein
        if lat and lon:
            stat.latitude = float(lat)
            stat.longitude = float(lon)
            
        stat.save()

        return Response({"message": f"Updated {city_name} successfully!"})

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def public_dashboard_stats(request):
    try:
        # 1. FAST CALCULATION: Database se direct sum nikalein (Loop ki zaroorat nahi)
        aggregates = DengueStat.objects.aggregate(
            total_active=Sum('active_cases'),
            total_recovered=Sum('recovered'),
            total_deaths=Sum('deaths')
        )

        # Agar DB khali ho to None ki jagah 0 use karein
        total_active = aggregates['total_active'] or 0
        total_recovered = aggregates['total_recovered'] or 0
        total_deaths = aggregates['total_deaths'] or 0

        # 2. MAP DATA PREPARATION
        # Sirf wo shehar uthayen jinki location set hai
        mapped_cities = DengueStat.objects.filter(
            latitude__isnull=False, 
            longitude__isnull=False
        )

        data = []
        for s in mapped_cities:
            data.append({
                "city_name": s.city_name,   # Frontend aksar 'city_name' expect karta hai
                "city": s.city_name,        # Backup key
                "latitude": s.latitude,     # Full spelling (Safe)
                "longitude": s.longitude,   # Full spelling (Safe)
                "lat": s.latitude,          # Short spelling (Backup)
                "lon": s.longitude,         # Short spelling (Backup)
                "active": s.active_cases,
                "recovered": s.recovered,
                "deaths": s.deaths
            })

        return Response({
            "overview": {
                "active": total_active,
                "recovered": total_recovered,
                "deaths": total_deaths
            },
            "stats": data,      # Standard naming convention
            "city_stats": data  # Aapke purane code ki compatibility ke liye
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
 