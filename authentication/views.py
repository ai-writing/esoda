from django.shortcuts import render
from django.contrib.auth.models import User
from forms import FieldSelectForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
# Create your views here.


# Views for profile urls
@login_required
def domain_view(request):
    user = User.objects.get(id=request.user.id)
    corpus_id = user.userprofile.corpus_id
    if request.method == 'POST':
        form = FieldSelectForm(request.POST)
        if form.is_valid():
            cid = form.cleaned_data['choice']
            if corpus_id != cid:  # need to update fid & cids
                user.userprofile.corpus_id = cid
                user.save()
            messages.success(request, _('Corpus update successfully'))
            # return redirect(reverse('field_select'))
    else:
        form = FieldSelectForm(initial={'choice': corpus_id})
    return render(request, "profile/domain_select.html", {'form': form, 'menu_index': 1, 'profileTab': 'domain'})


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
