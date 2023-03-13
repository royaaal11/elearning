from django.contrib import admin
from .models import \
    Teacher, Student, Subject, Quarter, Module, \
    LearningOutcome, Quiz, Assessment, QuizQuestion, \
    QuizChoice, AssessmentQuestion, AssessmentChoice, \
        VideoLesson, PerformanceTask

import nested_admin
    
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "designation")


class QuarterInline(admin.TabularInline):
    model = Quarter
    extra = 1


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    inlines = [QuarterInline]
    list_display = ("id", "title", "full_title", "teacher")


class LearningOutcomeInline(nested_admin.NestedTabularInline):
    model = LearningOutcome
    extra = 2


class VideoLessonInline(nested_admin.NestedTabularInline):
    model = VideoLesson
    extra = 1


class PerformanceTaskInline(nested_admin.NestedTabularInline):
    model = PerformanceTask
    extra = 1


@admin.register(Module)
class ModuleAdmin(nested_admin.NestedModelAdmin):
    inlines = [LearningOutcomeInline, VideoLessonInline, PerformanceTaskInline]
    # readonly_fields = ["status", "date_quiz_taken"]
    list_display = ("id", "name", "title", "description", "status", "duration", "quarter", "date_quiz_taken", "quiz_total")

    @admin.display(description="Quiz Items Total")
    def quiz_total(self, module):
        module_quizes = module.quiz_set.all()
        module_quizes_count = sum([m.quizquestion_set.all().count() for m in module_quizes])
        return module_quizes_count


class QuizChoiceInline(nested_admin.NestedTabularInline):
    model = QuizChoice
    extra = 4
    

class QuizQuestionInline(nested_admin.NestedTabularInline):
    model = QuizQuestion
    extra = 2
    inlines = [QuizChoiceInline]
    # readonly_fields = ["student_answer", "student_correct"]


@admin.register(Quiz)
class QuizAdmin(nested_admin.NestedModelAdmin):
    inlines = [QuizQuestionInline]
    list_display = ("id", "module", "title", "number_of_items")

    @admin.display(description="Total items")
    def number_of_items(self, quiz):
        return quiz.quizquestion_set.all().count()


class AssessmentChoiceInline(nested_admin.NestedTabularInline):
    model = AssessmentChoice
    extra = 4
    

class AssessmentQuestionInline(nested_admin.NestedTabularInline):
    model = AssessmentQuestion
    extra = 2
    inlines = [AssessmentChoiceInline]
    readonly_fields = ["student_answer", "student_correct"]


@admin.register(Assessment)
class AssessmentAdmin(nested_admin.NestedModelAdmin):
    inlines = [AssessmentQuestionInline]
    list_display = ("id", "quarter", "title")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__", "subject_list")
    
