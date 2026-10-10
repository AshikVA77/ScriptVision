from django.shortcuts import render, redirect
from Admin.models import *
from Guest.models import tbl_teacher
from Student.models import tbl_student

def Adminhome(request):
    if request.session.get("user_type") != "admin":
        return redirect("Guest:Login")
    
    department_count=tbl_department.objects.count()
    subject_count=tbl_subject.objects.count()
    teacher_count=tbl_teacher.objects.count()
    student_count=tbl_student.objects.count()

    return render(request, "Admin/Adminhome.html", {
        'department_count': department_count,
        'teacher_count': teacher_count,
        'student_count': student_count,
        'subject_count': subject_count
    })


def Departments(request):
    if request.session.get("user_type") != "admin":
        return redirect("Guest:Login")

    departments = tbl_department.objects.all()

    return render(request, "Admin/Departments.html", {
        "departments": departments
    })

def Teachers(request):
    if request.session.get("user_type") != "admin":
        return redirect("Guest:Login")

    teachers = tbl_teacher.objects.all()

    return render(request, "Admin/Teachers.html", {
        "teachers": teachers
    })


def Subjects(request):
    if request.session.get("user_type") != "admin":
        return redirect("Guest:Login")

    subjects = tbl_subject.objects.all()

    return render(request, "Admin/Subjects.html", {
        "subjects": subjects
    })

def Students(request):
    if request.session.get("user_type") != "admin":
        return redirect("Guest:Login")

    students = tbl_student.objects.all()

    return render(request, "Admin/Students.html", {
        "students": students
    })


def AddMaterials(request):

    departments = tbl_department.objects.all()

    if request.method == "POST":

        department_id = request.POST.get("department")
        material_title = request.POST.get("title")
        material_file = request.FILES.get("study_material")

        if not department_id or not material_title or not material_file:
            return render(
                request,
                "Admin/AddMaterials.html",
                {
                    "departments": departments,
                    "error": "Please fill all fields."
                }
            )

        department = tbl_department.objects.filter(
            dept_id=department_id
        ).first()

        if not department:
            return render(
                request,
                "Admin/AddMaterials.html",
                {
                    "departments": departments,
                    "error": "Invalid department selected."
                }
            )

        tbl_studymaterial.objects.create(
            material_title=material_title,
            material_file=material_file,
            material_department=department,
            material_status="Active"
        )

        return redirect("Admin:AddMaterials")

    return render(
        request,
        "Admin/AddMaterials.html",
        {
            "departments": departments
        }
    ) 

def AddDepartment(request):
    if request.session.get("user_type") != "admin":
        return redirect("Guest:Login")

    if request.method == "POST":
        tbl_department.objects.create(
            dept_name=request.POST.get("dept_name"),
            dept_code=request.POST.get("dept_code")
        )

        return redirect("Admin:Departments")

    return render(request, "Admin/AddDepartment.html")

def AddSubject(request):
    if request.session.get("user_type") != "admin":
        return redirect("Guest:Login")

    if request.method == "POST":
        tbl_subject.objects.create(
            subject_name=request.POST.get("subject_name"),
            subject_code=request.POST.get("subject_code"),
            subject_department_id=request.POST.get("department")
        )

        return redirect("Admin:Subjects")

    departments = tbl_department.objects.filter(
        dept_status="Active"
    )

    return render(request, "Admin/AddSubject.html", {
        "departments": departments
    })


def Logout(request):
    request.session.flush()
    return redirect("Guest:index")