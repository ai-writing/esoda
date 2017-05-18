# -*- coding: utf-8 -*-
from .models import Comment
from django.contrib.auth.models import User
from datetime import datetime


def get_feedbacks():
    feedbackList = []
    for i in Comment.objects.all():
        if i.display:
            feedbackList.append({
                'content': i.text,
                'user_name': i.user
            })
        if len(feedbackList) == 10:
            break
    return feedbackList


def save_message(request):
    msg = request.POST.get('message', '').strip()
    if msg and request.user.id:  # User post a message
        user = User.objects.get(id=request.user.id)
        c = Comment(text=msg, user=user, display=False, date=datetime.now())
        c.save()
