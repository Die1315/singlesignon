from django.urls import reverse
import json
from django import forms
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from polls import models
from polls.forms.user import ProfileForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@login_required
def index(request):
    print(request)
    filter = request.GET.get("search",False)
    context = {
        'polls': []
    }
    polls = models.Poll.objects.all()
    for poll in polls:
        if filter :
            polls_data = poll.answers.filter(value__icontains=filter)
        else:
            polls_data = poll.answers.all()
        item = {
            "title": poll.title,
            "id": poll.pk,
            "answers": [{
                "value": answer.value,
                "user_first_name": answer.user.first_name,
                "user_last_name": answer.user.last_name,
                "id": answer.pk,
            } for answer in polls_data ]
        }
        context['polls'].append(item)

    return render(request, 'polls/index.html', context)

@login_required
def my_profile(request):
    error=None
    current_user_profile = request.user.profile
    user_form = models.ProfileForm.objects.get(site=current_user_profile.site)
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            #print(request.POST)
            profile = models.Profile.objects.get(user=current_user_profile.user)
            profile.user.first_name=request.POST.get("first_name")
            profile.user.last_name=request.POST.get("last_name")
            for key in [field['id'] for field in user_form.form_fields['fields']]:
                #print(key)
                profile.dynamic_fields[key] = request.POST.get(key)
            profile.save()
            profile.user.save()
            return redirect(reverse("my_profile"))
        else:
            error = "No valido"
    
    fields = user_form.form_fields['fields']
    
    data = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
    }

    data.update(current_user_profile.dynamic_fields)
    print(data,fields)
    form = ProfileForm(fields=fields, initial=data)
    return render(request, 'polls/current_user.html', {'form': form, "error": error})

@login_required
@csrf_exempt
def edit_answer(request, poll_id, answer_id):
    payload = json.loads(request.body)
    answer = models.Answer.objects.get(pk=answer_id)
    answer.value = payload.get('value')
    answer.save()
    return JsonResponse({"value": answer.value})