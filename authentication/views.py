# This Python file uses the following encoding: utf-8
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.http import JsonResponse
import json
from esoda.utils import CORPUS
# Create your views here.

FIELD_NAME = [u'BNC',u'高性能计算', u'计算机网络', u'网络安全', u'软件工程', u'数据挖掘',
              u'计算机理论', u'计算机图形学', u'人工智能', u'人机交互',  u'交叉综合', u'全部']
# Views for profile urls
@login_required
def domain_view(request):
    user = User.objects.get(id=request.user.pk)
    corpus_id = user.userprofile.getid()
    if request.method == 'POST':
        cids=request.POST.getlist('ids')
        corpus_id=[0]*1000
        for i in cids:
            corpus_id[int(i)]=1
        user.userprofile.setid(corpus_id) 
        user.userprofile.save()
        messages.success(request, u'领域更新成功')
    node_tree=tree(corpus_id)
    return render(request, "profile/domain_select.html", {'menu_index': 1, 'profileTab': 'domain','corpus': node_tree})


def changed_child(request):
    cid = int(request.GET['id'])  
    try:
        index=tree_first.index(cid)
        children=tree_second[index]
    except:
        children=[]
    return JsonResponse(children, safe=False)

def search(request):
    result=[]
    expand=[]
    target=request.GET['target']
    if target=="":
        return JsonResponse(result, safe=False)
    user = User.objects.get(id=request.user.pk)
    corpus_id = user.userprofile.getid()
    node_tree=tree(corpus_id)
    for k in node_tree:
        for i in k.nodes:
            for j in i["nodes"]:
                if target.lower() in j["text"].lower():
                    result.append(j["id"])
                    if not i["id"] in expand:
                        expand.append(i["id"])
    return JsonResponse({"expand":expand,"result":result}, safe=False)

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
tree_first=[0, 2, 51, 74, 99, 145, 179, 208, 237, 280, 299]
field=["英国国家语料库","计算机科学与技术"]
field_list=[[u'BNC'],[u'高性能计算', u'计算机网络', u'网络安全', u'软件工程', u'数据挖掘',
              u'计算机理论', u'计算机图形学', u'人工智能', u'人机交互',  u'交叉综合']]
def get_dept_tree(corpus_id):
    tree_first=[]
    display_tree = []
    c_id=0;
    a_id=0;
    for k in range(len(field)):
        node0=TreeNode()
        node0.id=k
        node0.text=field[k]
        field_tree=[]
        node0.nodes=field_tree
        display_tree.append(node0)
        for i in range(len(field_list[k])):
            node = TreeNode()
            node.id = c_id
            node.text = field_list[k][i]
            tree_first.append(c_id)
            c_id+=1
            children = CORPUS[str(a_id)]
            a_id+=1
            tree_second_lef=[]
            for i in children:
                node1 = TreeNode()
                node1.id = c_id
                temp=i['i'].replace('conf/','')
                temp=temp.replace('journals/','')
                node1.text = temp
                tree_second_lef.append(c_id);
                c_id+=1
                node1.nodes = []
                node.nodes.append(node1.to_dict(corpus_id[node1.id]))
            tree_second.append(tree_second_lef)
            field_tree.append(node.to_dict(corpus_id[node.id]))
    # print tree_first
    return display_tree

def tree(corpus_id):
    tree = get_dept_tree(corpus_id)
    return tree

class TreeNode():
    def __init__(self):
        self.id = 0
        self.text = "Node 1"
        self.state = {
             'checked': False,
        }
        self.nodes = []
    def to_dict(self,checked):
        if checked==0:
            check=False
        else:
            check=True
        temp={
            'id': self.id,
            'text': self.text,
            'state': {'checked': checked}
        }
        if not len(self.nodes)==0:
            temp['nodes']=self.nodes
        return temp