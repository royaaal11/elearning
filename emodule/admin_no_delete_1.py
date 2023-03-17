from django.contrib import admin

import nested_admin

from .models import \
    Teacher, Student, Subject, Quarter, Module, \
    LearningOutcome, Quiz, Assessment, QuizQuestion, \
    QuizChoice, AssessmentQuestion, AssessmentChoice, \
        VideoLesson, PerformanceTask

    
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "designation")


class QuarterInline(admin.TabularInline):
    model = Quarter

    def get_extra(self, request, obj=None, **kwargs):
        print('obj:', obj)
        extra = 4
        if obj:
            return extra - obj.quarter_set.count()
        return extra


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    inlines = [QuarterInline]
    list_display = ("id", "title", "full_title", "teacher")


class LearningOutcomeInline(admin.TabularInline):
    model = LearningOutcome
    extra = 2


class VideoLessonInline(admin.TabularInline):
    model = VideoLesson
    extra = 1


class PerformanceTaskInline(admin.TabularInline):
    model = PerformanceTask
    extra = 1


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    inlines = [LearningOutcomeInline, VideoLessonInline, PerformanceTaskInline]
    # readonly_fields = ["status", "date_quiz_taken"]
    ordering = ("seqno",)
    list_display = ("seqno", "name", "title", "description", "duration", "quarter", "quiz_total")

    @admin.display(description="Quiz Items Total")
    def quiz_total(self, module):
        module_quizes = module.quiz_set.all()
        module_quizes_count = sum([m.quizquestion_set.all().count() for m in module_quizes])
        return module_quizes_count


# class QuizChoiceInline(admin.TabularInline):
#     model = QuizChoice
#     extra = 4
    

# class QuizQuestionInline(admin.TabularInline):
#     model = QuizQuestion
#     # extra = 2
#     inlines = [QuizChoiceInline]
#     # readonly_fields = ["student_answer", "student_correct"]

#     def get_extra(self, request, obj=None, **kwargs):
#         print('obj.quizquestion_set.count:', obj.quizquestion_set.count())
#         return 0 if obj else 1


# @admin.register(Quiz)
# class QuizAdmin(admin.ModelAdmin):
#     inlines = [QuizQuestionInline]
#     list_display = ("id", "module", "title", "number_of_items")

#     @admin.display(description="Total items")
#     def number_of_items(self, quiz):
#         return quiz.quizquestion_set.all().count()



class QuizChoiceInline(admin.TabularInline):
    model = QuizChoice

    def get_extra(self, request, obj=None, **kwargs):
        extra = 4
        if obj:
            return extra - obj.quizchoice_set.count()
        return extra

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    inlines = [QuizChoiceInline]

    # This will hide this Model from the admin interface
    def get_model_perms(self, request):
        return {}


class QuizQuestionLinInline(admin.TabularInline):
    model = QuizQuestion
    fields = ('text',)
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    inlines = [QuizQuestionLinInline]

    def response_add(self, request, obj):
        print('response_add direction', obj.direction)
        return super().response_add(request, obj)

    def response_change(self, request, obj):
        print('response_change')
        return super().response_change(request, obj)


class AssessmentChoiceInline(admin.TabularInline):
    model = AssessmentChoice
    extra = 4
    

class AssessmentQuestionInline(admin.TabularInline):
    model = AssessmentQuestion
    extra = 2
    inlines = [AssessmentChoiceInline]


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    inlines = [AssessmentQuestionInline]
    list_display = ("id", "quarter", "title")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__", "subject_list")


@admin.register(PerformanceTask)
class PerformanceTaskAdmin(admin.ModelAdmin):
    list_display = ("module", "title", "gdrive_link")


@admin.register(VideoLesson)
class VideoLessonAdmin(admin.ModelAdmin):
    list_display = ("module", "title", "video_url")
    
