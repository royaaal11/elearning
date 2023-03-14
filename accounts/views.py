from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

from .forms import SignUpForm
from emodule.models import Student, Subject


def signup_request(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            # load the profile instance created by the signal
            user.save()
            tle_subject = Subject.objects.all().first()
            new_student = Student.objects.create(user=user)
            new_student.subjects.add(tle_subject)
            new_student.save()
            raw_password = form.cleaned_data.get('password1')
            # login user after signing up
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)

            messages.info(request, f"You are now logged in as {user}.")
            # redirect user to home page
            return redirect(reverse('emodule:home'))
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.") 
    return redirect("accounts:login")


def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("emodule:home")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request, "accounts/login.html", context={"form":form})