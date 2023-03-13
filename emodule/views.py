from datetime import datetime

from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from . import configs, utils
from .models import *


class BaseView(LoginRequiredMixin, TemplateView):
    template_name = 'emodule/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = utils.update_context(context, utils.base_context())
        return context


class HomePage(BaseView):
    template_name = 'emodule/home.html'

    def get_context_data(self, **kwargs):
        student_user = Student.objects.get(user__id=self.request.user.id)
        context = super().get_context_data(**kwargs)
        context['test'] = Subject.objects.all()
        context['recent_module_list'] = Module.objects.filter(
            quarter__subject__student__id=student_user.id).order_by('-date_quiz_taken')[:5]
        print('context', context)
        return context


# class SubjectList(BaseView, ListView):
#     context_object_name = 'subject_list'
#     template_name = 'emodule/subject_list.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context

#     def get_queryset(self):
#         return {}


class SubjectDetail(BaseView, DetailView):
    template_name = 'emodule/subject_detail.html'
    model = Subject
    context_object_name = 'subject'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        quarter_list = list(self.get_object().quarter_set.all().order_by('seqno'))
        temp = []
        for idx, quarter in enumerate(quarter_list):
            temp1 = {
                "quarter": quarter,
                "prerequisite": quarter_list[idx - 1] if idx > 0 else None
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
        context = super().get_context_data(**kwargs)
        context['module_list'] = self.get_object().module_set.all()
        context['lesson_menu_active'] = True
        return context


class ModuleDetail(BaseView, DetailView):
    template_name = 'emodule/module/module_detail.html'
    model = Module
    context_object_name = 'module'

    def post(self, *args, **kwargs):
        context = self.get_context_data()
        module = self.get_object()
        post_data = self.request.POST
        models_for_saving = []

        try:
            # TODO: if you have time. refactor this :)
            if module.status == 'Not yet started':
                for quiz in module.quiz_list:
                    for question in quiz.quizquestion_set.all():
                        correct_answer = question.quizchoice_set.get(is_correct=True).text
                        form_answer = post_data.get('quiz_choice_{}'.format(question.id))
                        # mark student_correct field to True/False
                        question.student_correct = True if correct_answer == form_answer else False
                        # set the student_answer field to the form_answer value
                        question.student_answer = form_answer
                        models_for_saving.append(question)
                    quiz.date_taken = datetime.now()
                    models_for_saving.append(quiz)

                module.date_quiz_taken = datetime.now()
                module.status = MODULE_STATUS_CHOICES[0][0]
                models_for_saving.append(module)
            else:
                messages.info(self.request, "You have already completed this activity.")
        except:
            messages.error(self.request, "Something went wrong. Please try again.")
        else:
            for _model in models_for_saving:_model.save()
            messages.success(self.request, "Your activity has been submitted")
            return HttpResponseRedirect(reverse("emodule:module-detail", kwargs={"subject_id": module.quarter.subject.id, "quarter_id": module.quarter.id, "pk": module.id}))
        return render(self.request, self.template_name, context)

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        context['learning_outcomes'] = self.get_object().learningoutcome_set.all()
        context['other_modules_in_quarter'] = Module.objects.exclude(id=self.get_object().id)
        context['lesson_menu_active'] = True
        return context


class QuarterAssessmentDetail(BaseView, DetailView):
    template_name = 'emodule/assessment_detail.html'
    model = Quarter
    context_object_name = 'quarter'

    # TODO: if you have time. refactor this :)
    def post(self, *args, **kwargs):
        context = self.get_context_data()
        quarter = self.get_object()
        post_data = self.request.POST
        models_for_saving = []

        try:
            if quarter.status == 'Not yet started':
                for assessment in quarter.assessment_list:
                    for question in assessment.assessmentquestion_set.all():
                        correct_answer = question.assessmentchoice_set.get(is_correct=True).text
                        form_answer = post_data.get('assessment_choice_{}'.format(question.id))
                        question.student_correct = True if correct_answer == form_answer else False
                        question.student_answer = form_answer
                        models_for_saving.append(question)
                    assessment.date_taken = datetime.now()
                    models_for_saving.append(assessment)

                quarter.date_assessment_taken = datetime.now()
                quarter.status = MODULE_STATUS_CHOICES[0][0]
                models_for_saving.append(quarter)
            else:
                messages.info(self.request, "You have already completed this assessment.")
        except:
            messages.error(self.request, "Something went wrong. Please try again.")
        else:
            for _model in models_for_saving: _model.save()
            messages.success(self.request, "Your assessment has been submitted")
            return HttpResponseRedirect(reverse("emodule:assessment-detail", kwargs={"subject_id": quarter.subject.id, "pk": quarter.id, "page_type":"assessment"}))
        return render(self.request, self.template_name, context)

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        context['next_quarter_assessment'] = Quarter.objects.get(seqno=self.get_object().id + 1)
        context['lesson_menu_active'] = True
        return context

