# This Python file uses the following encoding: utf-8
from django.shortcuts import render
from django.contrib.auth.models import User
from forms import FieldSelectForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from models import Corpus,TreeNode
from django.http import JsonResponse
import json
# Create your views here.


# Views for profile urls
@login_required
def domain_view(request):
    user = User.objects.get(id=request.user.id)
    corpus_id = user.userprofile.getid()
    if request.method == 'POST':
        cid = int(request.POST['id'])
        corpus=Corpus.objects.get(c_id=cid)
        result=1-corpus_id[cid] # need to update fid & cids
        children=get_children(corpus)
        for i in children:
            corpus_id[i]=result
        user.userprofile.setid(corpus_id) 
        user.userprofile.save()
        # messages.success(request, u'领域更新成功')
            # return redirect(reverse('field_select'))
    return render(request, "profile/domain_select.html", {'menu_index': 1, 'profileTab': 'domain','tree': tree})

def get_children(corpus):
    result=[]
    result+=[corpus.c_id]  
    children = corpus.children.all()
    for ch in children:
        result+=get_children(ch)
    return result

def changed_child(request):
    cid = int(request.GET['id'])
    corpus=Corpus.objects.get(c_id=cid)
    children=get_children(corpus)
    children=children[1:len(children)]
    return JsonResponse(children, safe=False)

def personal_view(request):
    info = {
        'profileTab': 'personal'
    }
    return render(request, 'profile/personal.html', info)


def favorites_view(request):
    exampleList = []
    for i in range(1, 51):
        exampleList.append({
            'content': 'The crucial <strong>quality</strong> of this active assimilation was that it guaranteed a certain depth in the individual meteorologist\'s interpretation of the information.',
            'source': 'UIST\'07. M. Morris et. al.SearchTogether: an interface for collaborative web search.',
            'heart_number': 129,
        })

    info = {
        'example_number': 50,
        'search_time': 0.1,
        'exampleList': exampleList,
        'profileTab': 'favorites'
    }
    return render(request, 'profile/favorites.html', info)


def get_dept_tree(parents,corpus_id):
    display_tree = []
    for p in parents:
        node = TreeNode()
        node.id = p.c_id
        node.text = p.name
        children = p.children.all()
        if len(children) > 0:
            node.nodes = get_dept_tree(children,corpus_id)
        display_tree.append(node.to_dict(corpus_id[node.id]))
    return display_tree

def tree(request):
    root = Corpus.objects.get(parent=None)
    user = User.objects.get(id=request.user.id)
    corpus_id = user.userprofile.getid()
    tree = get_dept_tree([root],corpus_id)
    return JsonResponse(tree, safe=False)