from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.contrib.auth.models import User
from .models import QuizProfile, Question, AttemptedQuestion, Choice
from .forms import UserLoginForm, RegistrationForm, GuestUserForm

def home(request):
    context = {}
    return render(request, 'game/home.html', context=context)

@login_required
def user_home(request):
    context = {}
    return render(request, 'game/user_home.html', context=context)

def leaderboard(request):
    top_quiz_profiles = QuizProfile.objects.order_by('-total_score')[:500]
    total_count = top_quiz_profiles.count()
    context = {
        'top_quiz_profiles': top_quiz_profiles,
        'total_count': total_count,
    }
    return render(request, 'game/leaderboard.html', context=context)

@login_required()
def play(request):
    quiz_profile, created = QuizProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        question_pk = request.POST.get('question_pk')
        attempted_question = quiz_profile.attempts.select_related('question').get(question__pk=question_pk)
        choice_pk = request.POST.get('choice_pk')

        try:
            selected_choice = attempted_question.question.choices.get(pk=choice_pk)
        except ObjectDoesNotExist:
            raise Http404

        quiz_profile.evaluate_attempt(attempted_question, selected_choice)
        return redirect('game:submission_result', attempted_question_pk=attempted_question.pk)
    else:
        question = quiz_profile.get_new_question()
        if question is not None:
            quiz_profile.create_attempt(question)

        context = {
            'question': question,
        }
        return render(request, 'game/play.html', context=context)

@login_required()
def submission_result(request, attempted_question_pk):
    attempted_question = get_object_or_404(AttemptedQuestion, pk=attempted_question_pk)
    context = {
        'attempted_question': attempted_question,
    }
    return render(request, 'game/submission_result.html', context=context)

def login_view(request):
    title = "Prisijungti"
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('game:user_home')
            else:
                form.add_error(None, "Vartotojas neaktyvus")
        else:
            form.add_error(None, "Neteisingas vartotojo vardas arba slaptažodis")

    # Grąžiname šabloną, jei forma nėra validi arba POST užklausa nepavyko
    return render(request, 'game/login.html', {"form": form, "title": title})



def register(request):
    title = "Sukurti naują paskyrą"
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('game:login')
    else:
        form = RegistrationForm()

    context = {'form': form, 'title': title}
    return render(request, 'game/registration.html', context=context)

def logout_view(request):
    logout(request)
    return redirect('game:home')

def guest_login(request):
    if request.method == 'POST':
        form = GuestUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            guest_user, created = User.objects.get_or_create(username=username)
            if created:
                guest_user.set_unusable_password()
                guest_user.save()
            quiz_profile, created = QuizProfile.objects.get_or_create(user=guest_user)
            login(request, guest_user)
            return redirect('game:play')
    else:
        form = GuestUserForm()
    return render(request, 'game/guest_login.html', {'form': form})

def about(request):
    return render(request, 'game/about.html')