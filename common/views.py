from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import logging

from .models import Comment


logger = logging.getLogger(__name__)


def comment_view(request):
    msg = request.POST.get('message', '').strip()
    if msg:
        request.session.save()
        comment = Comment(text=msg, display=settings.DEBUG, session=request.session.session_key)
        if request.user.is_authenticated:
            comment.user = request.user
        comment.save()
        logger.info('%s %s %s %s %s', request.META.get('REMOTE_ADDR', '0.0.0.0'), request.session.session_key, request.user, request, msg)
    return JsonResponse({'success': True})
