from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
import traceback
from .agent import run_agent 

@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message")
            
            if not request.session.session_key:
                request.session.save()
            
            thread_id = request.session.session_key or str(uuid.uuid4())

            profile = None
            if request.user.is_authenticated:
                try:
                    profile = request.user.profile
                except:
                    pass

            print(f"--- START AI ---")
            print(f"Message: {user_message}")
            print(f"Thread ID: {thread_id}")

            ai_odpoved = run_agent(user_message, thread_id, profile)

            return JsonResponse({"response": ai_odpoved})
            
        except Exception as e:
            print("\n CRITICAL ERROR: ")
            traceback.print_exc() 
            print(" ---------------------------------------\n")
            
            return JsonResponse({"error": str(e)}, status=500)
            
    return JsonResponse({"error": "Method not allowed"}, status=405)