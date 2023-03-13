from django.urls import path
from . import views

app_name = 'emodule'

urlpatterns = [
    # homepage
    path('', views.HomePage.as_view(), name='index'),
    path('home/', views.HomePage.as_view(), name='home'),

    # list of subjects
    # path('subjects/', views.SubjectList.as_view(), name='subjects'),

    # subject detail - list of quarters
    path('subject/<int:pk>/', views.SubjectDetail.as_view(), name='subject-detail'),
    # path('subject/<int:subject_id>/', views.subject_detail_view, name='subject-detail'),

    # quarter detail - list of modules
    path('subject/<int:subject_id>/<int:pk>/', views.QuarterDetail.as_view(), name='quarter-detail'),

    # module detail
    path('subject/<int:subject_id>/<int:quarter_id>/<int:pk>/', views.ModuleDetail.as_view(), name='module-detail'),

    # assessment detail
    path('subject/<int:subject_id>/<int:pk>/<str:page_type>/', views.QuarterAssessmentDetail.as_view(), name='assessment-detail'),
]