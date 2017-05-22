from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Comment


def comment_view(request):
    msg = request.POST.get('message', '').strip()
    if msg:
        request.session.save()
        comment = Comment(text=msg, session = request.session.session_key, display = True)
        if request.user.is_authenticated:
            comment.user = request.user
        comment.save()
    	return JsonResponse({'success': True})
    return JsonResponse({})
