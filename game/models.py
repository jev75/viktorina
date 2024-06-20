import random
from django.db import models
from django.contrib.auth.models import User
from model_utils.models import TimeStampedModel


class Question(TimeStampedModel):
    ALLOWED_NUMBER_OF_CORRECT_CHOICES = 1

    html = models.TextField(verbose_name='Klausimas')
    is_published = models.BooleanField(default=False, null=False, verbose_name='Ar paskelbtas')
    maximum_marks = models.DecimalField(default=4, decimal_places=2, max_digits=6, verbose_name='Maksimalūs balai')

    class Meta:
        verbose_name = 'Klausimas'
        verbose_name_plural = 'Klausimai'

    def __str__(self):
        return self.html

class Choice(TimeStampedModel):
    MAX_CHOICES_COUNT = 4

    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE, verbose_name='Klausimas')
    is_correct = models.BooleanField(default=False, null=False, verbose_name='Ar teisingas')
    html = models.TextField(verbose_name='Atsakymas')

    class Meta:
        verbose_name = 'Pasirinkimas'
        verbose_name_plural = 'Pasirinkimai'

    def __str__(self):
        return self.html

class QuizProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Vartotojas')
    total_score = models.DecimalField(default=0, decimal_places=2, max_digits=10, verbose_name='Bendras balas')

    class Meta:
        verbose_name = 'Profilis'
        verbose_name_plural = 'Profiliai'

    def __str__(self):
        return f'Vartotojas: {self.user}'

    def get_new_question(self):
        used_questions_pk = AttemptedQuestion.objects.filter(quiz_profile=self).values_list('question__pk', flat=True)
        remaining_questions = Question.objects.exclude(pk__in=used_questions_pk).filter(is_published=True)
        if not remaining_questions.exists():
            return None
        return random.choice(remaining_questions)

    def create_attempt(self, question):
        attempted_question = AttemptedQuestion(question=question, quiz_profile=self)
        attempted_question.save()

    def evaluate_attempt(self, attempted_question, selected_choice):
        if attempted_question.question_id != selected_choice.question_id:
            return

        attempted_question.selected_choice = selected_choice
        if selected_choice.is_correct:
            attempted_question.is_correct = True
            attempted_question.marks_obtained = attempted_question.question.maximum_marks

        attempted_question.save()
        self.update_score()

    def update_score(self):
        marks_sum = self.attempts.filter(is_correct=True).aggregate(
            models.Sum('marks_obtained'))['marks_obtained__sum']
        self.total_score = marks_sum or 0
        self.save()

class AttemptedQuestion(TimeStampedModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Klausimas')
    quiz_profile = models.ForeignKey(QuizProfile, on_delete=models.CASCADE, related_name='attempts',
                                     verbose_name='Profilis')
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, verbose_name='Pasirinkimas')
    is_correct = models.BooleanField(default=False, null=False, verbose_name='Ar teisingas')
    marks_obtained = models.DecimalField(default=0, decimal_places=2, max_digits=6, verbose_name='Gauti balai')

    class Meta:
        verbose_name = 'Bandytas klausimas'
        verbose_name_plural = 'Bandyti klausimai'

    def get_absolute_url(self):
        return f'Rezultatai:{self.pk}'