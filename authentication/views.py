# This Python file uses the following encoding: utf-8
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.http import JsonResponse
import json
from esoda.utils import CORPUS2ID
# Create your views here.

FIELD_NAME = [u'BNC',u'高性能计算', u'计算机网络', u'网络安全', u'软件工程', u'数据挖掘',
              u'计算机理论', u'计算机图形学', u'人工智能', u'人机交互',  u'交叉综合', u'全部']
# Views for profile urls
@login_required
def domain_view(request):
    user = User.objects.get(id=request.user.id)
    corpus_id = user.userprofile.getid()
    if request.method == 'POST':
        cid = int(request.POST['id'])      
        result=1-corpus_id[cid] # need to update fid & cids
        corpus_id[cid]=result
        try:
            index=tree_first.index(cid)
            children=tree_second[index]
            for i in children:
                corpus_id[i]=result
        except:
            pass
        user.userprofile.setid(corpus_id) 
        user.userprofile.save()
        # messages.success(request, u'领域更新成功')
            # return redirect(reverse('field_select'))
    return render(request, "profile/domain_select.html", {'menu_index': 1, 'profileTab': 'domain','tree': tree})


def changed_child(request):
    cid = int(request.GET['id'])  
    try:
        index=tree_first.index(cid)
        children=tree_second[index]
    except:
        children=[]
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


tree_second=[]
tree_first=[]

def get_dept_tree(corpus_id):
    display_tree = []
    c_id=0;
    for i in range(0,11):
        node = TreeNode()
        node.id = c_id
        node.text = FIELD_NAME[i]
        tree_first.append(c_id)
        c_id+=1
        children = CORPUS2ID[str(i)]
        tree_second_lef=[]
        for i in children:
            node1 = TreeNode()
            node1.id = c_id
            node1.text = i['i']
            tree_second_lef.append(c_id);
            c_id+=1
            node1.nodes = []
            node.nodes.append(node1.to_dict(corpus_id[node1.id]))
        tree_second.append(tree_second_lef)
        display_tree.append(node.to_dict(corpus_id[node.id]))
    return display_tree

def tree(request):
    user = User.objects.get(id=request.user.id)
    corpus_id = user.userprofile.getid()
    tree = get_dept_tree(corpus_id)
    return JsonResponse(tree, safe=False)

class TreeNode():
    def __init__(self):
        self.id = 0
        self.text = "Node 1"
        self.href = "#node-1"
        self.selectable = True
        self.state = {
             'checked': False,
        }
        self.tags = ['available']
        self.nodes = []
    def to_dict(self,checked):
        if checked==0:
            check=False
        else:
            check=True
        icon = (len(self.nodes) > 0) and 'glyphicon glyphicon-list-alt' or 'glyphicon glyphicon-user'
        return {
            'id': self.id,
            'text': self.text,
            'icon': icon,
            'tags': ['1'],
            'nodes': self.nodes,
            'state': {'checked': check, 'expanded':False}
        }