from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('dashboard/',dashbaord),
    path('my-profile/',profile),


    # auth routes
    path('login/',loginUser),
    path('register/',register),
    path('logout/',logoutUser),

    # classes routes
    path('classes/',classes),
    path('class/details/<int:id>',classDetails),
    path('my-classes/',myClasses),
    path('enrolled-classes/<int:id>',enrolledClasses),
    path('enroll/class/<int:class_id>',enrollToClass),
    path('payment-page/',paymentPage),
    path('submit-payment/<int:enroll_id>', submitPayment),
    path('edit-class-model-meet-link/<int:class_id>', editClassMeetLink),
    path('post-resources/<int:class_id>', postResources),

    path('update-course-syllabus/<int:course_id>', update_course_syllabus),
]
