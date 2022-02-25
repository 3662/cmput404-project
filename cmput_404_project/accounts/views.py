from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages

from django.urls import reverse_lazy
from django.views import generic

from .forms import AuthorCreationForm
from social_distribution.models import Author



def signup_request(request):
    if request.method == 'POST':
        form = AuthorCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            profile_image = form.cleaned_data['profile_image']
            host = f"{request.scheme}://{request.get_host()}/"
            github = form.cleaned_data['github']
            author = Author.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, profile_image=profile_image, host=host, github=github)
            login(request, author)
            messages.success(request, 'Signup successful.')
            return redirect('home')
        messages.error(request, 'Unsuccessful signup. Invalid information')
    form = AuthorCreationForm()
    return render(request=request, template_name='registration/signup.html', context={'form': form})


