from django.contrib import admin
from .models import Question, Choice, QuizProfile, AttemptedQuestion
from .forms import QuestionForm, ChoiceForm, ChoiceInlineFormset


class ChoiceInline(admin.TabularInline):
    model = Choice
    can_delete = False
    max_num = Choice.MAX_CHOICES_COUNT
    min_num = Choice.MAX_CHOICES_COUNT
    form = ChoiceForm
    formset = ChoiceInlineFormset
    extra = 0


class QuestionAdmin(admin.ModelAdmin):
    form = QuestionForm
    inlines = (ChoiceInline,)
    list_display = ['html', 'is_published', 'maximum_marks']
    list_filter = ['is_published']
    search_fields = ['html', 'choices__html']
    actions = ['publish_questions', 'unpublish_questions']

    def publish_questions(self, request, queryset):
        queryset.update(is_published=True)
    publish_questions.short_description = "Paskelbti pasirinktas klausimus"

    def unpublish_questions(self, request, queryset):
        queryset.update(is_published=False)
    unpublish_questions.short_description = "Atšaukti pasirinktas klausimus"

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['created', 'modified']
        return []


class QuizProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_score']
    search_fields = ['user__username', 'total_score']
    readonly_fields = ['total_score']
    actions = None


class AttemptedQuestionAdmin(admin.ModelAdmin):
    list_display = ['question', 'quiz_profile', 'selected_choice', 'is_correct', 'marks_obtained']
    list_filter = ['is_correct']
    search_fields = ['question__html', 'quiz_profile__user__username', 'selected_choice__html']
    readonly_fields = ['marks_obtained']
    actions = None


admin.site.register(Question, QuestionAdmin)
admin.site.register(QuizProfile, QuizProfileAdmin)
admin.site.register(AttemptedQuestion, AttemptedQuestionAdmin)
