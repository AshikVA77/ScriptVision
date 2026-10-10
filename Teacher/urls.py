from django.urls import path
from Teacher import views

app_name = 'Teacher'

urlpatterns = [

    path('', views.Teacherhome, name='Teacherhome'),
    path('CreateExam/', views.CreateExam, name='CreateExam'),
    path('Questions/', views.Questions, name='Questions'),
    path('AddQuestions/<int:exam_id>/', views.AddQuestions, name='AddQuestions'),
    path('UploadScripts/', views.UploadScripts, name='UploadScripts'),
    path('SelectStudent/<int:exam_id>/',views.SelectStudent,name='SelectStudent'),
    path('Logout/', views.Logout, name='Logout'),
    path('Evaluate/<int:stdexam_id>/', views.EvaluateScript, name='EvaluateScript'),
    path('ExamResults/', views.ExamResults, name='ExamResults'),
    path('ExamStudents/<int:exam_id>/',views.ExamStudents,name='ExamStudents'),
    path("TeacherFeedback/", views.TeacherFeedback, name="TeacherFeedback"),
    path("TeacherProfile/", views.TeacherProfile, name="TeacherProfile"),
    path("EditTeacherProfile/", views.EditTeacherProfile, name="EditTeacherProfile"),
    path('publish-exam-results/<int:exam_id>/',views.PublishExamResults,name='PublishExamResults'),

]