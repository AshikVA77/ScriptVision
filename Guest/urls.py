from django.urls import path
from Guest import views
app_name = 'Guest'

urlpatterns = [
    path('', views.index, name='index'),
    path("Studentregister/", views.Studentregister, name="Studentregister"),
    path("Teacherregister/", views.Teacherregister, name="Teacherregister"),
    path("Register/",views.Register,name="Register"),
    path("Login/", views.Login, name="Login"),
    path("About/", views.About, name="About"),
    path("FAQ/", views.FAQ, name="FAQ"),
    path("Contact/", views.Contact, name="Contact"),
    
]
