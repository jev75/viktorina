from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, get_user_model
from .models import Question, Choice

class GuestUserForm(forms.Form):
    username = forms.CharField(max_length=150, label='Vartotojo vardas', required=True)

# Esamos formos
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['html', 'is_published']
        widgets = {
            'html': forms.Textarea(attrs={'rows': 3, 'cols': 80}),
        }
        labels = {
            'html': 'HTML turinys',
            'is_published': 'Ar paskelbtas'
        }

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['html', 'is_correct']
        widgets = {
            'html': forms.Textarea(attrs={'rows': 2, 'cols': 80}),
        }
        labels = {
            'html': 'HTML turinys',
            'is_correct': 'Ar teisingas'
        }

class ChoiceInlineFormset(forms.BaseInlineFormSet):
    def clean(self):
        super(ChoiceInlineFormset, self).clean()
        correct_choices_count = 0
        for form in self.forms:
            if not form.is_valid():
                return
            if form.cleaned_data and form.cleaned_data.get('is_correct') is True:
                correct_choices_count += 1
        try:
            assert correct_choices_count == Question.ALLOWED_NUMBER_OF_CORRECT_CHOICES
        except AssertionError:
            raise forms.ValidationError('Leidžiamas vienas teisingas pasirinkimas.')

User = get_user_model()

class UserLoginForm(forms.Form):
    username = forms.CharField(label='Vartotojo vardas')
    password = forms.CharField(widget=forms.PasswordInput, label='Slaptažodis')

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Tokio vartotojo nėra")
            if not user.check_password(password):
                raise forms.ValidationError("Neteisingas slaptažodis")
            if not user.is_active:
                raise forms.ValidationError("Vartotojas neaktyvus")
        return super(UserLoginForm, self).clean(*args, **kwargs)

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='El. paštas')
    first_name = forms.CharField(required=True, label='Vardas')
    last_name = forms.CharField(required=True, label='Pavardė')

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]
        labels = {
            'username': 'Vartotojo vardas',
            'first_name': 'Vardas',
            'last_name': 'Pavardė',
            'email': 'El. paštas',
            'password1': 'Slaptažodis',
            'password2': 'Pakartokite slaptažodį',
        }

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
