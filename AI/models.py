from django.db import models

# Create your models here.
class tbl_aievaluationlog(models.Model):
    log_id = models.AutoField(primary_key=True)
    answerscript = models.ForeignKey('Teacher.tbl_answerscript', on_delete=models.CASCADE)
    process_name = models.CharField(max_length=100)
    model_used = models.CharField(max_length=100)
    processing_status = models.CharField(max_length=20, default='Pending')
    processing_time = models.FloatField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.process_name} - {self.answerscript.script_id}"