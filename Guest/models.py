from django.db import models
from Admin.models import *

# Create your models here.
class tbl_teacher(models.Model):
    teacher_id = models.AutoField(primary_key=True)
    teacher_name = models.CharField(max_length=100)
    teacher_email = models.EmailField(max_length=100)
    teacher_password = models.CharField(max_length=100)
    teacher_phone = models.CharField(max_length=15)
    teacher_department = models.CharField(max_length=100)
    teacher_profile_pic = models.ImageField(upload_to='Assets/Teachers/', null=True, blank=True)
    teacher_status = models.CharField(max_length=10, default='Active')
    th_created_at = models.DateTimeField(auto_now_add=True,null=True)
    th_updated_at = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return self.teacher_name

class tbl_student(models.Model):
    student_id = models.AutoField(primary_key=True)
    student_name = models.CharField(max_length=100)
    student_email = models.EmailField(max_length=100)
    student_password = models.CharField(max_length=100)
    student_phone = models.CharField(max_length=15)
    student_department = models.CharField(max_length=100)
    student_profile_pic = models.ImageField(upload_to='Assets/Students/', null=True, blank=True)
    student_status = models.CharField(max_length=10, default='Active')
    st_creted_at = models.DateTimeField(auto_now_add=True,null=True)
    st_updated_at = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return self.student_name

class tbl_contact_message(models.Model):
    Message_id = models.AutoField(primary_key=True)
    Message_name = models.CharField(max_length=100)
    Message_email = models.EmailField(max_length=100)
    Message_subject = models.CharField(max_length=100)
    Message_content = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True,null=True)
    status = models.CharField(max_length=10, default='Unread')