from django.db import models
from Guest.models import *
from Admin.models import *

# Create your models here.
class tbl_studentfeedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(tbl_student, on_delete=models.CASCADE)
    result = models.ForeignKey('Teacher.tbl_result', on_delete=models.CASCADE)
    student_comment = models.TextField()
    reply = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    reply_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.student_name} - {self.result.result_id}"

class tbl_student_subject(models.Model):

    enrollment_id = models.AutoField(primary_key=True)

    student = models.ForeignKey(
        'Guest.tbl_student',
        on_delete=models.CASCADE
    )

    subject = models.ForeignKey(
        'Admin.tbl_subject',
        on_delete=models.CASCADE
    )

    enrolled_date = models.DateTimeField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=10,
        default="Active"
    )

    class Meta:
        unique_together = ('student', 'subject')

    def __str__(self):
        return f"{self.student.student_name} - {self.subject.subject_name}"