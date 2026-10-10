from django.shortcuts import render,redirect
from Guest.models import *
from Admin.models import *

# Create your views here.

def index(request):
    
    return render(request, 'Guest/index.html')

def Studentregister(request):
    if request.method == "POST":
        tbl_student.objects.create( student_name = request.POST.get('sdname'),
               student_email = request.POST.get('sdemail'),
               student_password = request.POST.get('sdpassword'), 
               student_phone = request.POST.get('sdphone'),
               student_department = request.POST.get('sddepartment'),
               student_profile_pic = request.FILES.get('sdprofile_pic'))
        return redirect('Guest:Login')
    else:
        return render(request, 'Guest/Studentregister.html')

def Teacherregister(request):
    if request.method == "POST":
        tbl_teacher.objects.create( teacher_name = request.POST.get('thname'),
               teacher_email = request.POST.get('themail'),
               teacher_password = request.POST.get('thpassword'), 
               teacher_phone = request.POST.get('thphone'),
               teacher_department = request.POST.get('thdepartment'),
               teacher_profile_pic = request.FILES.get('thprofile_pic'))
        return redirect('Guest:Login')
    else:
        return render(request, 'Guest/Teacherregister.html')

def Login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        student = tbl_student.objects.filter(
            student_email=email,
            student_password=password
        ).first()

        if student:
            request.session["user_id"] = student.student_id
            request.session["user_type"] = "student"
            return redirect("Student:Studenthome")

        teacher = tbl_teacher.objects.filter(
            teacher_email=email,
            teacher_password=password
        ).first()

        if teacher:
            request.session["user_id"] = teacher.teacher_id
            request.session["user_type"] = "teacher"
            return redirect("Teacher:Teacherhome")

        admin = tbl_admin.objects.filter(
            admin_email=email,
            admin_password=password
        ).first()

        if admin:
            request.session["user_id"] = admin.admin_id
            request.session["user_type"] = "admin"
            return redirect("Admin:Adminhome")

        return render(request, "Guest/Login.html", {
            "error_message": "Invalid email or password."
        })

    return render(request, "Guest/Login.html")

def About(request):
    return render(request, 'Guest/About.html')

def FAQ(request):
    return render(request, 'Guest/FAQ.html')

def Contact(request):
    return render(request, 'Guest/Contact.html')

def Register(request):

    if request.method == "POST":

        role = request.POST.get("role")

        if role == "student":

            password = request.POST.get("sdpassword")
            confirm_password = request.POST.get("sdconfirm_password")

            if password != confirm_password:
                return render(request, "Guest/Register.html", {
                    "error": "Password and Confirm Password do not match."
                })

            tbl_student.objects.create(
                student_name=request.POST.get("sdname"),
                student_email=request.POST.get("sdemail"),
                student_password=password,
                student_phone=request.POST.get("sdphone"),
                student_department=request.POST.get("sddepartment"),
                student_profile_pic=request.FILES.get("sdprofile_pic")
            )

            return redirect("Guest:Login")


        elif role == "teacher":

            password = request.POST.get("thpassword")
            confirm_password = request.POST.get("thconfirm_password")

            if password != confirm_password:
                return render(request, "Guest/Register.html", {
                    "error": "Password and Confirm Password do not match."
                })

            tbl_teacher.objects.create(
                teacher_name=request.POST.get("thname"),
                teacher_email=request.POST.get("themail"),
                teacher_password=password,
                teacher_phone=request.POST.get("thphone"),
                teacher_department=request.POST.get("thdepartment"),
                teacher_profile_pic=request.FILES.get("thprofile_pic")
            )

            return redirect("Guest:Login")


    return render(request, "Guest/Register.html")