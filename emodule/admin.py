from django.contrib import admin
from django.utils.html import format_html, format_html_join

import nested_admin

from .models import \
    Teacher, Student, Subject, Quarter, Module, \
    LearningOutcome, Quiz, Assessment, QuizQuestion, \
    QuizChoice, AssessmentQuestion, AssessmentChoice, \
        VideoLesson, PerformanceTask, StudentAssessmentResult, StudentQuizResult

    
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "designation")


class QuarterInline(admin.TabularInline):
    model = Quarter

    def get_extra(self, request, obj=None, **kwargs):
        extra = 4
        if obj:
            return extra - obj.quarter_set.count()
        return extra


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    inlines = [QuarterInline]
    list_display = ("id", "title", "full_title", "teacher")


class LearningOutcomeInline(nested_admin.NestedTabularInline):
    model = LearningOutcome
    extra = 2


class VideoLessonInline(nested_admin.NestedTabularInline):
    model = VideoLesson
    extra = 0


class PerformanceTaskInline(nested_admin.NestedTabularInline):
    model = PerformanceTask
    extra = 0


@admin.register(Module)
class ModuleAdmin(nested_admin.NestedModelAdmin):
    inlines = [LearningOutcomeInline, VideoLessonInline, PerformanceTaskInline]
    # readonly_fields = ["status", "date_quiz_taken"]
    ordering = ("seqno",)
    list_display = ("seqno", "name", "title", "description", "duration", "quarter", "quiz_total")

    @admin.display(description="Quiz Items Total")
    def quiz_total(self, module):
        module_quizes = module.quiz_set.all()
        module_quizes_count = sum([m.quizquestion_set.all().count() for m in module_quizes])
        return module_quizes_count


class QuizChoiceInline(nested_admin.NestedTabularInline):
    model = QuizChoice
    extra = 2
    

class QuizQuestionInline(nested_admin.NestedTabularInline):
    model = QuizQuestion
    extra = 2
    inlines = [QuizChoiceInline]

    # def get_extra(self, request, obj=None, **kwargs):
    #     return 0 if obj else 1


@admin.register(Quiz)
class QuizAdmin(nested_admin.NestedModelAdmin):
    inlines = [QuizQuestionInline]
    list_display = ("id", "module", "title", "number_of_items")

    @admin.display(description="Total items")
    def number_of_items(self, quiz):
        return quiz.quizquestion_set.all().count()


class AssessmentChoiceInline(nested_admin.NestedTabularInline):
    model = AssessmentChoice
    extra = 2
    

class AssessmentQuestionInline(nested_admin.NestedTabularInline):
    model = AssessmentQuestion
    extra = 2
    inlines = [AssessmentChoiceInline]


@admin.register(Assessment)
class AssessmentAdmin(nested_admin.NestedModelAdmin):
    inlines = [AssessmentQuestionInline]
    list_display = ("id", "quarter", "number_of_items")

    @admin.display(description="Total items")
    def number_of_items(self, assessment):
        return assessment.assessmentquestion_set.all().count()


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__",
                    "score_quarter_1", "score_quarter_2", "score_quarter_3" ,"score_quarter_4")
 
    def _get_quarter_scores(self, quarter_seqno, student_id, type):
        quarter_assessment = StudentAssessmentResult.objects\
                    .filter(quarter__seqno=quarter_seqno)\
                    .filter(student__id=student_id)\
                    .order_by("-group")
        quarter_modules = Module.objects.filter(quarter__seqno=quarter_seqno)
        module_results = []

        for module in quarter_modules:
            # check first if a module has an activity
            if module.quiz_set.all():
                result = StudentQuizResult.objects\
                    .filter(module__seqno=module.seqno)\
                    .filter(student__id=student_id)\
                    .order_by("-group")
                module_results.append((
                    module.title, 
                    result.first().score if result else None, 
                    result.first().status if result else None)
                )

        final_result = []
        passed = 'green'
        failed = 'red'
        for result_set in module_results:
            status = ''
            if result_set[2] == 'Passed':
                status = passed
            elif result_set[2] == 'Failed':
                status = failed
            final_result.append((status, result_set[0], result_set[1]))

        assessment_status = ''
        if quarter_assessment and quarter_assessment.first().status == 'Passed':
            assessment_status = passed
        elif quarter_assessment and quarter_assessment.first().status == 'Failed':
            assessment_status = failed

        # Prepend the assessment scores per quarter
        final_result = [(assessment_status, 'Assessment', quarter_assessment.first().score if quarter_assessment else None)] + final_result
        return format_html_join("\n", "<li style='color: {}'>{} - {}</li>", ((result[0], result[1], result[2]) for result in final_result))

    @admin.display(description="1st Quarter")
    def score_quarter_1(self, student):
        return self._get_quarter_scores(1, student.id, 'assessment')
    
    @admin.display(description="2nd Quarter")
    def score_quarter_2(self, student):
        return self._get_quarter_scores(2, student.id, 'assessment')
    
    @admin.display(description="3rd Quarter")
    def score_quarter_3(self, student):
        return self._get_quarter_scores(3, student.id, 'assessment')
    
    @admin.display(description="4th Quarter")
    def score_quarter_4(self, student):
        return self._get_quarter_scores(4, student.id, 'assessment')

admin.site.site_header = 'Basketry Admin'