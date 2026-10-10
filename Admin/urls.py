from django.urls import path
from Admin import views

app_name = "Admin"

urlpatterns = [
    path("", views.Adminhome, name="Adminhome"),
    path("Departments/", views.Departments, name="Departments"),
    path("AddDepartment/", views.AddDepartment, name="AddDepartment"),
    path("AddSubject/", views.AddSubject, name="AddSubject"),
    path("AddMaterials/", views.AddMaterials, name="AddMaterials"),
    path("Subjects/", views.Subjects, name="Subjects"),
    path("Teachers/", views.Teachers, name="Teachers"),
    path("Students/", views.Students, name="Students"),
    path("Logout/", views.Logout, name="Logout"),
]