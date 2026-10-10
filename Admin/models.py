from django.db import models


# Create your models here.

class tbl_admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    admin_name = models.CharField(max_length=100)
    admin_email = models.EmailField(max_length=100)
    admin_password = models.CharField(max_length=100)

    def __str__(self):
        return self.admin_name


class tbl_department(models.Model):
    dept_id= models.AutoField(primary_key=True)
    dept_name = models.CharField(max_length=100)
    dept_code = models.CharField(max_length=10)
    dept_status = models.CharField(max_length=10, default='Active')

class tbl_subject(models.Model):
    subject_id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=100)
    subject_code = models.CharField(max_length=10)
    subject_status = models.CharField(max_length=10, default='Active')
    subject_department = models.ForeignKey(tbl_department, on_delete=models.CASCADE)

class tbl_studymaterial(models.Model):
    material_id = models.AutoField(primary_key=True)
    material_title = models.CharField(max_length=200)
    material_file = models.FileField(upload_to="study_materials/")
    material_department = models.ForeignKey(tbl_department, on_delete=models.CASCADE)
    uploaded_date = models.DateTimeField(auto_now_add=True)
    material_status = models.CharField(max_length=10, default="Active")

    def __str__(self):
        return self.material_title