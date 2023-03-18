from datetime import datetime

from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from . import configs, utils
from .models import *


class BaseView(LoginRequiredMixin, TemplateView):
    template_name = 'emodule/base.html'

    def get_current_student(self):
        return Student.objects.get(user__id=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = utils.update_context(context, utils.base_context())
        context['search_source'] = Module.objects.all()
        return context
    

class ActivityBaseDetail(BaseView, DetailView):
    type = '' # assessment or quiz
    model = '' # Quarter or Module
    redirect_to_after_submit = "" # url name to go to after submitting activity

    def build_activity_list(self):
        # Hierarchy:
        # group_type_obj -> activity_group -> activity -> questions -> choice
        # eg. Module -> Quiz - 1 -> True/False -> True/False Question 1 -> Question 1 choices
        group_type_obj = self.get_object()
        activity_group = {} # Group of questions. A module or assessment can have multiple types i.e. True/False or Multiple Choice
        _activity_group = group_type_obj.assessment_set.all() if self.type == 'assessment' else group_type_obj.quiz_set.all()
        
        # recreate the group list
        for activity in _activity_group:
            activity_id = "activity_{}".format(activity.id)
            question_list = {}

            # create the question object then map the student's answer per question if there are any
            activity_questions = activity.assessmentquestion_set.all() if self.type == 'assessment' else activity.quizquestion_set.all()
            for question in activity_questions:
                question_id = "question_{}".format(question.id)

                # get the student's latest answer for this question
                if self.type == 'assessment':
                    student_answer = StudentQuestionAnswers.objects.\
                        filter(student=self.get_current_student()).\
                        filter(assessment_question=question).\
                        order_by("-group").first()
                else:
                    student_answer = StudentQuizQuestionAnswers.objects.\
                        filter(student=self.get_current_student()).\
                        filter(quiz_question=question).\
                        order_by("-group").first()
                
                question_list[question_id] = {
                    "question_obj": question,
                    "student_answer": student_answer
                }

            activity_group[activity_id] = {
                "activity_obj": activity,
                "question_list": question_list
            }
        return activity_group
    
    def post(self, *args, **kwargs):
        context = self.get_context_data()
        group_type_obj = self.get_object()
        post_data = self.request.POST
        models_for_saving = []
        correct_answer_count = 0

        # check first if the student already took the assessment or quiz.
        if self.type == 'assessment':
            done_with_activity = StudentAssessmentResult.objects\
                .filter(quarter=group_type_obj)\
                .filter(student=self.get_current_student())
        else:
            done_with_activity = StudentQuizResult.objects\
                .filter(module=group_type_obj)\
                .filter(student=self.get_current_student())
        
        if not done_with_activity:
            try:
                _activity_group = group_type_obj.assessment_list if self.type == 'assessment' else group_type_obj.quiz_list
                for activity in _activity_group:

                    activity_questions = activity.assessmentquestion_set.all() if self.type == 'assessment' else activity.quizquestion_set.all()
                    for question in activity_questions:
                        correct_answer = int(question.assessmentchoice_set.get(is_correct=True).id) if self.type == 'assessment' else int(question.quizchoice_set.get(is_correct=True).id)
                        form_answer = post_data.get('{}_choice_{}'.format(self.type, question.id))
                        if form_answer:
                            form_answer = int(form_answer)
                        else:
                            raise TypeError

                        # TODO: this is very inefficient for large data. but it's not part of the agreement :)
                        result_model = StudentAssessmentResult if self.type == 'assessment' else StudentQuizResult
                        latest_result = result_model.objects.all().order_by("-group").first()
                        next_group_id = latest_result.group + 1 if latest_result else 1
                        is_correct = False
                        
                        if correct_answer == form_answer:
                            is_correct = True
                            correct_answer_count += 1

                        if self.type == 'assessment':
                            student_answer = StudentQuestionAnswers (
                                assessment_question=question,
                                student=self.get_current_student(),
                                answer_id=form_answer,
                                is_correct=is_correct,
                                group=next_group_id
                            )
                        else:
                            student_answer = StudentQuizQuestionAnswers (
                            quiz_question=question,
                            student=self.get_current_student(),
                            answer_id=form_answer,
                            is_correct=is_correct,
                            group=next_group_id
                        )

                        models_for_saving.append(student_answer)
                
                activity_total_count = group_type_obj.assessment_count if self.type == 'assessment' else group_type_obj.quiz_count
                passing_score = (settings.PASSING_PERCENTAGE/100) * activity_total_count

                if self.type == 'assessment':
                    student_result = StudentAssessmentResult (
                        quarter=group_type_obj,
                        student=self.get_current_student(),
                        score=correct_answer_count,
                        date_taken=datetime.now(),
                        group=next_group_id,
                        status=configs.ACTIVITY_STATUS[0][0] if correct_answer_count >= passing_score else configs.ACTIVITY_STATUS[1][0]
                    )
                else:
                    student_result = StudentQuizResult (
                        module=group_type_obj,
                        student=self.get_current_student(),
                        score=correct_answer_count,
                        date_taken=datetime.now(),
                        group=next_group_id,
                        status=configs.ACTIVITY_STATUS[0][0] if correct_answer_count >= passing_score else configs.ACTIVITY_STATUS[1][0]
                    )

                models_for_saving.append(student_result)
            except TypeError:
                messages.error(self.request, "You cannot leave a question blank.")
            except:
                messages.error(self.request, "Something went wrong. Please try again or contact your adviser. Thank you")
            else:
                if settings.ALLOW_SAVE_TO_DB:
                    for _model in models_for_saving: _model.save()
                messages.success(self.request, "Your assessment has been submitted" if self.type == 'assessment' else "Your activity has been submitted")
            finally:
                return HttpResponseRedirect(reverse(self.redirect_to_after_submit, kwargs=kwargs))
        else:
            messages.info(self.request, "You are done with this already.")
        return render(self.request, self.template_name, context)


class HomePage(BaseView):
    template_name = 'emodule/home.html'

    def get_context_data(self, **kwargs):
        student_user = Student.objects.get(user__id=self.request.user.id)
        context = super().get_context_data(**kwargs)
        recent_quiz_attempts = StudentQuizResult.objects.filter(student=student_user).order_by("-group")[:5]
        context['recent_quiz_attempts'] = recent_quiz_attempts
        return context


class ModuleDetail(ActivityBaseDetail):
    template_name = 'emodule/module/module_detail.html'
    model = Module
    type = 'quiz'
    redirect_to_after_submit = "emodule:module-detail"
    context_object_name = 'module'

    def _get_templates(self):
        module = self.get_object()
        # <lesson_type>_<quarter_seqno>_<module_title>.html
        template = '{}_{}_{}.html'
        quarter_seqno = 'quarter_{}'.format(module.quarter.seqno)
        module_title = utils.emodule_slugify(module.title, '_')

        lesson_template = template.format('lesson', module.quarter.seqno, module_title)
        video_template = template.format('video', module.quarter.seqno, module_title)
        performance_task_template = template.format('performance_task', module.quarter.seqno, module_title)

        base_dir = 'emodule/module/{}/{}/{}'
        return {
            'lesson_template': base_dir.format(quarter_seqno, module_title, lesson_template),
            'video_template': base_dir.format(quarter_seqno, module_title, video_template),
            'performance_task_template': base_dir.format(quarter_seqno, module_title, performance_task_template)
        }
    
    def get_other_modules_in_quarter(self):
        other_modules = []
        for module in self.get_object().quarter.module_set.exclude(id=self.get_object().id):
            other_modules.append({
                "module_obj": module,
                "latest_result": StudentQuizResult.objects\
                        .filter(module=self.get_object())\
                        .filter(student=self.get_current_student())
            })
        return other_modules

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        context['quiz_list'] = self.build_activity_list()
        context['quiz_score'] = StudentQuizResult.objects\
            .filter(student=self.get_current_student())\
            .filter(module=self.get_object())
        context['learning_outcomes'] = self.get_object().learningoutcome_set.all()
        context['latest_result'] = StudentQuizResult.objects\
            .filter(module=self.get_object())\
            .filter(student=self.get_current_student())
        context['other_modules_in_quarter'] = self.get_other_modules_in_quarter()
        context['lesson_templates'] = self._get_templates()
        context['lesson_menu_active'] = True
        return context


class SubjectDetail(BaseView, DetailView):
    template_name = 'emodule/subject_detail.html'
    model = Subject
    context_object_name = 'subject'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        student_user = self.get_current_student()
        context = super().get_context_data(**kwargs)
        quarter_list = list(self.get_object().quarter_set.all().order_by('seqno'))
        temp = []
        for idx, quarter in enumerate(quarter_list):
            temp1 = {
                "quarter": quarter,
                "assessment_result": StudentAssessmentResult.objects\
                    .filter(quarter=quarter)\
                    .filter(student=student_user),
                "prerequisite": quarter_list[idx - 1] if idx > 0 else None,
                "prerequisite_result": StudentAssessmentResult.objects\
                    .filter(quarter=quarter)\
                    .filter(student=student_user) if idx > 0 else None
            }
            temp.append(temp1)
        context['quarter_list'] = temp
        context['lesson_menu_active'] = True
        context = utils.update_context(context, utils.base_context())
        return context


class QuarterDetail(BaseView, DetailView):
    template_name = 'emodule/quarter_detail.html'
    model = Quarter
    context_object_name = 'quarter'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        student_user = self.get_current_student()
        context = super().get_context_data(**kwargs)
        module_list = []
        for module in self.get_object().module_set.all():
            module_detail = {
                "obj": module,
                "result": StudentQuizResult.objects\
                    .filter(module=module)\
                    .filter(student=student_user)
            }
            module_list.append(module_detail)
        context['module_list'] = module_list
        context['lesson_menu_active'] = True
        return context


class QuarterAssessmentDetail(ActivityBaseDetail):
    template_name = 'emodule/assessment_detail.html'
    model = Quarter
    type = 'assessment'
    redirect_to_after_submit = "emodule:assessment-detail"
    context_object_name = 'quarter'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        current_seqno = self.get_object().seqno
        context = super().get_context_data(**kwargs)
        context['assessment_list'] = self.build_activity_list()
        context['assessment_score'] = StudentAssessmentResult.objects\
            .filter(student=self.get_current_student())\
            .filter(quarter=self.get_object()).order_by('-group').first()
        context['next_quarter_assessment'] = Quarter.objects.filter(seqno=current_seqno + 1).first()
        context['previous_quarter_assessment'] = Quarter.objects.filter(seqno=current_seqno - 1).first()
        context['latest_result'] = StudentAssessmentResult.objects\
            .filter(quarter=self.get_object())\
            .filter(student=self.get_current_student()).order_by('-group').first()
        context['lesson_menu_active'] = True
        return context

