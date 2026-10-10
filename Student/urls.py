from django.urls import path
from Student import views
app_name = 'Student'

urlpatterns = [
    path('', views.Studenthome, name='Studenthome'),
    path("Logout/", views.Logout, name="Logout"),
    path("ViewResult/", views.ViewResult, name="ViewResult"),
    path("Aifeedback/<int:id>/", views.Aifeedback, name="Aifeedback"),
    path("Report/<int:id>/", views.Report, name="Report"),
    path("SelectSubject/", views.SelectSubject, name="SelectSubject"),
    path("SubjectResult/<int:subject_id>/", views.SubjectResult, name="SubjectResult"),
    path('StudyMaterials/', views.StudyMaterials, name='StudyMaterials'),
    path("StudentFeedback/", views.StudentFeedback, name="StudentFeedback"),
    path("StudentProfile/", views.StudentProfile, name="StudentProfile"),
    path("EditStudentProfile/", views.EditStudentProfile, name="EditStudentProfile"),
    path("DownloadResult/", views.DownloadResult, name="DownloadResult"),
]
