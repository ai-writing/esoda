from django.shortcuts import render
from django.contrib.auth.models import User
from forms import FieldSelectForm
# Create your views here.

# Views for profile urls
def domain_view(request):
    user = User.objects.get(id=request.user.id)
    corpus_id = user.userwithcorpus.corpus_id
    saved = False
    if request.method == 'POST':
        form = FieldSelectForm(request.POST)
        if form.is_valid():
            cid = form.cleaned_data['choice']
            if corpus_id != cid: # need to update fid & cids
                user.userwithcorpus.corpus_id = cid
                user.save();
            saved = True    # saved successfully
            # return redirect(reverse('field_select'))
    else:
        form = FieldSelectForm(initial={'choice': corpus_id})
    return render(request, "profile/domain_select.html", {'form': form, 'menu_index': 1, 'saved': saved,'profileTab': 'domain'})

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

