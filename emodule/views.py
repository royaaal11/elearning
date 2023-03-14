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
        return context


class HomePage(BaseView):
    template_name = 'emodule/home.html'

    def get_context_data(self, **kwargs):
        student_user = Student.objects.get(user__id=self.request.user.id)
        context = super().get_context_data(**kwargs)
        recent_quiz_attempts = StudentQuizResult.objects.filter(student=student_user).order_by("-group")[:5]
        context['recent_quiz_attempts'] = recent_quiz_attempts
        print("recent_quiz_attempts:", recent_quiz_attempts)
        return context


# class SubjectList(BaseView, ListView):
#     context_object_name = 'subject_list'
#     template_name = 'emodule/subject_list.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context

#     def get_queryset(self):
#         return {}


class ModuleDetail(BaseView, DetailView):
    template_name = 'emodule/module/module_detail.html'
    model = Module
    context_object_name = 'module'

    def build_quiz_list(self):
        module = self.get_object()
        quiz_list = {}
        _quiz_list = module.quiz_set.all()
        
        # create the quiz list
        for quiz in _quiz_list:
            quiz_id = "quiz_{}".format(quiz.id)
            question_list = {}

            # create the quiz object
            for question in quiz.quizquestion_set.all():
                question_id = "question_{}".format(question.id)

                # get the student's latest answer for this question
                student_answer = StudentQuizQuestionAnswers.objects.\
                    filter(student=self.get_current_student()).\
                    filter(quiz_question=question).\
                    order_by("-group").first()
                
                question_list[question_id] = {
                    "question_obj": question,
                    "student_answer": student_answer
                }

            quiz_list[quiz_id] = {
                "quiz_obj": quiz,
                "question_list": question_list
            }
        return quiz_list

    def post(self, *args, **kwargs):
        context = self.get_context_data()
        module = self.get_object()
        post_data = self.request.POST
        models_for_saving = []
        correct_answer_count = 0

        # check first if the student already took the quiz.
        done_with_quiz = StudentQuizResult.objects\
            .filter(module=module)\
            .filter(student=self.get_current_student())
        
        if not done_with_quiz:
            try:
                for quiz in module.quiz_list:
                    for question in quiz.quizquestion_set.all():
                        correct_answer = int(question.quizchoice_set.get(is_correct=True).id)
                        form_answer = post_data.get('quiz_choice_{}'.format(question.id))
                        if form_answer:
                            form_answer = int(form_answer)
                        else:
                            raise TypeError

                        # TODO: this is very inefficient for large data. but this is just for demo so should be fine :)
                        latest_result = StudentQuizResult.objects.all().order_by("-group").first()
                        next_group_id = latest_result.group + 1 if latest_result else 1
                        is_correct = False
                        
                        if correct_answer == form_answer:
                            is_correct = True
                            correct_answer_count += 1

                        student_answer = StudentQuizQuestionAnswers (
                            quiz_question=question,
                            student=self.get_current_student(),
                            answer_id=form_answer,
                            is_correct=is_correct,
                            group=next_group_id
                        )

                        models_for_saving.append(student_answer)

                passing_score = (settings.PASSING_PERCENTAGE/100) * module.quiz_count
                student_result = StudentQuizResult (
                    module=module,
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
                messages.error(self.request, "Something went wrong. Please try again.")
            else:
                for _model in models_for_saving: _model.save()
                messages.success(self.request, "Your quiz has been submitted")
                return HttpResponseRedirect(reverse("emodule:module-detail", kwargs=kwargs))
        else:
            messages.info(self.request, "You are already done with this quiz.")
        return render(self.request, self.template_name, context)
    
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
        context['quiz_list'] = self.build_quiz_list()
        context['quiz_score'] = StudentQuizResult.objects\
            .filter(student=self.get_current_student())\
            .filter(module=self.get_object())
        context['learning_outcomes'] = self.get_object().learningoutcome_set.all()
        context['latest_result'] = StudentQuizResult.objects\
            .filter(module=self.get_object())\
            .filter(student=self.get_current_student())
        context['other_modules_in_quarter'] = self.get_other_modules_in_quarter()
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


class QuarterAssessmentDetail(BaseView, DetailView):
    template_name = 'emodule/assessment_detail.html'
    # template_name = 'emodule/test.html'
    model = Quarter
    context_object_name = 'quarter'

    def build_assessment_list(self):
        quarter = self.get_object()
        assessment_list = {}
        _assessment_list = quarter.assessment_set.all()
        
        # create the assessment list
        for assessment in _assessment_list:
            assessment_id = "assessment_{}".format(assessment.id)
            question_list = {}

            # create the question object
            for question in assessment.assessmentquestion_set.all():
                question_id = "question_{}".format(question.id)

                # get the student's latest answer for this question
                student_answer = StudentQuestionAnswers.objects.\
                    filter(student=self.get_current_student()).\
                    filter(assessment_question=question).\
                    order_by("-group").first()
                
                question_list[question_id] = {
                    "question_obj": question,
                    "student_answer": student_answer
                }

            assessment_list[assessment_id] = {
                "assessment_obj": assessment,
                "question_list": question_list
            }
        return assessment_list
        
    # TODO: if you have time. refactor this :)
    def post(self, *args, **kwargs):
        context = self.get_context_data()
        quarter = self.get_object()
        post_data = self.request.POST
        models_for_saving = []
        correct_answer_count = 0

        # check first if the student already took the assessment.
        done_with_assessment = StudentAssessmentResult.objects\
            .filter(quarter=quarter)\
            .filter(student=self.get_current_student())
        if not done_with_assessment:
            try:
                for assessment in quarter.assessment_list:
                    for question in assessment.assessmentquestion_set.all():
                        correct_answer = int(question.assessmentchoice_set.get(is_correct=True).id)
                        form_answer = post_data.get('assessment_choice_{}'.format(question.id))
                        if form_answer:
                            form_answer = int(form_answer)
                        else:
                            raise TypeError

                        # TODO: this is very inefficient for large data. but this is just for demo so should be fine :)
                        latest_result = StudentAssessmentResult.objects.all().order_by("-group").first()
                        next_group_id = latest_result.group + 1 if latest_result else 1
                        is_correct = False
                        
                        if correct_answer == form_answer:
                            is_correct = True
                            correct_answer_count += 1

                        student_answer = StudentQuestionAnswers (
                            assessment_question=question,
                            student=self.get_current_student(),
                            answer_id=form_answer,
                            is_correct=is_correct,
                            group=next_group_id
                        )

                        models_for_saving.append(student_answer)

                passing_score = (settings.PASSING_PERCENTAGE/100) * quarter.assessment_count
                student_result = StudentAssessmentResult (
                    quarter=quarter,
                    student=self.get_current_student(),
                    score=correct_answer_count,
                    date_taken=datetime.now(),
                    group=next_group_id,
                    status=configs.ACTIVITY_STATUS[0][0] if correct_answer_count >= passing_score else configs.ACTIVITY_STATUS[1][0]
                )
                models_for_saving.append(student_result)
            except:
                messages.error(self.request, "Something went wrong. Please try again.")
            else:
                for _model in models_for_saving: _model.save()
                messages.success(self.request, "Your assessment has been submitted")
                return HttpResponseRedirect(reverse("emodule:assessment-detail", kwargs=kwargs))
        else:
            messages.info(self.request, "You are already done with this assessment.")
        return render(self.request, self.template_name, context)

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        current_seqno = self.get_object().seqno
        context = super().get_context_data(**kwargs)
        context['assessment_list'] = self.build_assessment_list()
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

