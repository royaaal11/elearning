from django.contrib.auth.models import User
from django.conf import settings
from django.db import models

ACTIVITY_TYPE_CHOICES = (
    ("Quiz", "Quiz"),
    ("Assessment", "Assessment"),
)

MODULE_STATUS_CHOICES = (
    ("Complete", "Complete"),
    ("Not yet started", "Not yet started"),
    ("No activity", "No activity"),
)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    

class Teacher(Profile):
    designation = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name_plural = "1. Teacher"

    def __str__(self):
        return "{} ({})".format(self.full_name(), self.designation)
    
    def full_name(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)


class Subject(models.Model):
    title = models.CharField(max_length=200)
    full_title = models.CharField(max_length=200)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "2. Subjects"

    def __str__(self):
        return self.title
    
    def quarter_list(self):
        return 
    

class Student(Profile):
    subjects = models.ManyToManyField(Subject)

    class Meta:
        verbose_name_plural = "6. Students"


    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)
    
    def subject_list(self):
        return "\n".join([s.title for s in self.subjects.all()])


class Quarter(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    name = models.CharField(max_length=200) # e.g. TLE Quarter 1
    title = models.CharField(max_length=200) # e.g. 1st Quarter
    other_title = models.CharField(max_length=200) # e.g. Quarter 1
    status = models.CharField(max_length=200, choices=MODULE_STATUS_CHOICES, default="Not yet started") # e.g. Complete
    date_assessment_taken = models.DateTimeField(null=True, blank=True)
    seqno = models.IntegerField()

    def __str__(self):
        return self.name
    
    @property
    def assessment_list(self):
        return Quarter.objects.get(id=self.id).assessment_set.all()
    
    @property
    def assessment_total_score(self):
        assessment_list = self.assessment_list
        return sum([m.assessmentquestion_set.filter(student_correct=True).count() for m in assessment_list])
    
    @property
    def assessment_count(self):
        assessment_list = self.assessment_list
        return sum([m.assessmentquestion_set.all().count() for m in assessment_list])
    
    @property
    def student_passed(self):
        passing_score = self.assessment_total_score * (settings.PASSED_PERCENTAGE/100)
        return True if self.assessment_total_score > passing_score else False

class Module(models.Model):
    quarter = models.ForeignKey(Quarter, on_delete=models.CASCADE)
    name = models.CharField(max_length=200) # e.g. TLE 9-10 BASKETRY Q1_M0
    title = models.CharField(max_length=200) # e.g. History or Unit 1 or Unit 2
    description = models.CharField(max_length=200) # e.g. History of Basket weaving
    module_lesson = models.CharField(max_length=200, null=True, blank=True) # e.g. Enumerate Different Kinds of Macrame and Basketry Products
    unit_of_competency = models.CharField(max_length=200, null=True, blank=True) # e.g. ENUMERATE DIFFERENT KINDS OF MACRAME AND BASKETRY PRODUCTS
    duration = models.CharField(max_length=200, null=True, blank=True) # e.g. 5 days
    status = models.CharField(max_length=200, choices=MODULE_STATUS_CHOICES, default="Not yet started") # e.g. Complete
    date_quiz_taken = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "3. Modules"

    def __str__(self):
        return self.title
    
    @property
    def quiz_list(self):
        return Module.objects.get(id=self.id).quiz_set.all()
    
    @property
    def quiz_total_score(self):
        quiz_list = self.quiz_list
        return sum([m.quizquestion_set.filter(student_correct=True).count() for m in quiz_list])

    @property
    def quiz_count(self):
        quiz_list = self.quiz_list
        return sum([m.quizquestion_set.all().count() for m in quiz_list])
    

class LearningOutcome(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    text = models.CharField(max_length=200) # e.g. Enumerate Different Kinds of Macrame and Basketry Products, Describe different products of macrame nad basketry

    def __str__(self):
        return self.text


class Quiz(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True, null=True)
    direction = models.CharField(max_length=200)
    date_taken = models.DateTimeField(auto_now=True) #ignore this field. use the data_quiz_taken field in Module model

    class Meta:
        verbose_name_plural = "4. Quizzes"

    def __str__(self):
        return str(self.id)


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    student_answer = models.CharField(max_length=200, blank=True, null=True) # (Student's Answer) will be filled out once user has submitted the quiz
    student_correct = models.BooleanField(blank=True, null=True) # (Is the student's answer corret?) will be filled out once user has submitted the quiz


class QuizChoice(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField()


class Assessment(models.Model):
    quarter = models.ForeignKey(Quarter, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True, null=True)
    direction = models.CharField(max_length=200)
    date_taken = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "5. Assessments"


class AssessmentQuestion(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    student_answer = models.CharField(max_length=200, blank=True, null=True) # (Student's Answer) will be filled out once user has submitted the quiz
    student_correct = models.BooleanField(blank=True, null=True) # (Is the student's answer corret?) will be filled out once user has submitted the quiz


class AssessmentChoice(models.Model):
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField()


class VideoLesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True, null=True)
    video_url = models.URLField(max_length=200, verbose_name="Video URL")

    def __str__(self):
        return self.title
    

class PerformanceTask(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    gdrive_link = models.URLField(max_length=200, verbose_name="Google Drive Link")

    def __str__(self):
        return self.title
    

class QuarterAssessmentResult(models.Model):
    quarter = models.ForeignKey(Quarter, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.IntegerField()
    date_taken = models.DateTimeField()
