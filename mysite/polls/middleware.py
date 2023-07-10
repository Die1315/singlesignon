from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from polls import models

def is_profile_complete(user):
    site = user.profile.site
    form = models.ProfileForm.objects.get(site=site)
    form_fields = form.form_fields['fields']
    required_fields = [field['id'] for field in form_fields if field['required']]
    field_choices = [(field['choices'],field['id']) for field in form_fields if 'choices' in field]
    # print(field_choices)     
    is_complete = all([field in user.profile.dynamic_fields for field in required_fields])
    if is_complete:
        is_valid =all([user.profile.dynamic_fields[field[1]] in [label[0]  for label in field[0]] 
                       for field in field_choices 
                       ] )
    print(is_complete and is_valid)
    return is_complete and is_valid

class ProfileRedirectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        current_user = request.user
        skip_urls = [
            '/polls/myprofile',
            '/accounts/logout/',
        ]

        if (
            current_user.is_authenticated
            and request.path not in skip_urls
            and not is_profile_complete(current_user)
        ):
            return HttpResponseRedirect(reverse_lazy("my_profile"))
