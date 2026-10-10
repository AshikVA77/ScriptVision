from django.db import models
from Guest.models import *

# Create your models here.
class tbl_exam(models.Model):
    exam_id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(tbl_teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(tbl_subject, on_delete=models.CASCADE)
    exam_name = models.CharField(max_length=100)
    exam_type = models.CharField(max_length=50)
    exam_date = models.DateField()
    academic_year = models.CharField(max_length=20)
    total_marks = models.IntegerField()
    exam_status = models.CharField(max_length=10, default='Active')
    created_at = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.exam_name

class tbl_question(models.Model):
    question_id = models.AutoField(primary_key=True)
    exam = models.ForeignKey(tbl_exam, on_delete=models.CASCADE)
    question_number = models.CharField(max_length=10)
    question_text = models.TextField()

    question_figure = models.ImageField(
        upload_to='Assets/QuestionFigures/',
        blank=True,
        null=True
    )

    model_answer = models.TextField()

    model_answer_figure = models.ImageField(
        upload_to='Assets/ModelAnswerFigures/',
        blank=True,
        null=True
    )

    keywords = models.TextField(blank=True, null=True)
    maximum_marks = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Question {self.exam.exam_name} - {self.question_number}"

class tbl_stdexam(models.Model):
    stdexam_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(tbl_student, on_delete=models.CASCADE)
    exam = models.ForeignKey(tbl_exam, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, default='Pending')
    assigned_date = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return f"{self.student.student_name} - {self.exam.exam_name}"

class tbl_answerscript(models.Model):
    script_id = models.AutoField(primary_key=True)
    stdexam = models.ForeignKey(tbl_stdexam, on_delete=models.CASCADE)
    uploaded_file = models.FileField(upload_to='Assets/AnswerScripts/',blank=True, null=True)
    file_type = models.CharField(max_length=10, blank=True, null=True)
    total_pages = models.IntegerField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True,null=True)
    status = models.CharField(max_length=10, default='Pending')

    def __str__(self):
        return f"{self.stdexam.student.student_name} - {self.stdexam.exam.exam_name}"

class tbl_evaluation(models.Model):
    evaluation_id = models.AutoField(primary_key=True)
    answerscript = models.ForeignKey(tbl_answerscript, on_delete=models.CASCADE)
    question = models.ForeignKey(tbl_question, on_delete=models.CASCADE)
    page_number = models.IntegerField()
    extracted_text = models.TextField()
    similarity_score = models.FloatField(blank=True, null=True)
    ai_score = models.FloatField(blank=True, null=True)
    teacher_score = models.FloatField(blank=True, null=True)
    final_mark = models.FloatField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    evaluation_status = models.CharField(max_length=10, default='Pending')
    evaluated_at = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return f"{self.answerscript.stdexam.student.student_name} - {self.question.question_number}"

class tbl_result(models.Model):
    result_id = models.AutoField(primary_key=True)
    stdexam = models.ForeignKey(tbl_stdexam, on_delete=models.CASCADE)
    total_ai_marks = models.FloatField(blank=True, null=True)
    total_teacher_marks = models.FloatField(blank=True, null=True)
    total_final_marks = models.FloatField(blank=True, null=True)
    grade = models.CharField(max_length=5, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    published = models.BooleanField(default=False)
    published_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.stdexam.student.student_name} - {self.stdexam.exam.exam_name}"
