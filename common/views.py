from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Comment


def comment_view(request):
    msg = request.POST.get('message', '').strip()
    if msg:
        request.session.save()
        comment = Comment(text=msg, display=settings.DEBUG, session=request.session.session_key)
        if request.user.is_authenticated:
            comment.user = request.user
        comment.save()
    return JsonResponse({'success': True})
