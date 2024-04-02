from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils import timezone


# Create your models here.
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('teacher', _('Teacher')),
        ('student', _('Student')),
        ('super admin', _('Super Admin')),
    )
    user = models.OneToOneField(
        User, 
        verbose_name=_("user"), 
        on_delete=models.CASCADE
    )
    role = models.CharField(_("role"), max_length=12, choices=ROLE_CHOICES, default='', blank=True)
    profile = models.FileField(upload_to='profile/', null=True, blank=True)

class ClassModel(models.Model):
    name = models.CharField(max_length=50,default='class')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_classes',limit_choices_to={'userprofile__role': 'teacher'})
    syllabus = models.TextField(verbose_name=_("Syllabus"), blank=True)
    price = models.FloatField(verbose_name=_("Price"), blank=True,default = 0)
    class_time = models.CharField(max_length=20,blank=True,default=None)
    meet_link = models.CharField(max_length=500, verbose_name=_("Meet Link"), blank=True)

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    def __str__(self):
        return f"{self.name} Class taught by {self.teacher}"
    
class EnrolledStudent(models.Model):
    class_status_choices = (
        ('cannot_attended', _('Cannot Attended')),
        ('can_attend', _('Can Attend')),
    )

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrolled_classes',limit_choices_to={'userprofile__role': 'student'})
    class_enrolled = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name='enrolled_students')
    status = models.CharField(max_length=20, choices=class_status_choices, default='cannot_attended')
    full_name = models.CharField(max_length=100, default='')
    phone_number = models.CharField(max_length=20, default='')
    parent_name = models.CharField(max_length=100, default='')
    parent_phone_number = models.CharField(max_length=20, default='')
    address = models.CharField(max_length=20, default='')
    created_date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('student', 'class_enrolled')

class EnrollmentPayment(models.Model):
    enrollment = models.ForeignKey(EnrolledStudent, on_delete=models.CASCADE, related_name="payments")
    payment_proof = models.FileField(upload_to='payments/', null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.enrollment.full_name} - {self.timestamp}"

class ClassroomResource(models.Model):
    class_model = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name='classroom_resources')
    resource_file = models.FileField(upload_to='classroom_resources/',blank=True)
    message = models.TextField(blank=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_resources',null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    class Meta:
        verbose_name = 'Classroom Resource'
        verbose_name_plural = 'Classroom Resources'

class Testimonial(models.Model):
    image = models.FileField(upload_to='testimonials/')
    designation = models.CharField(max_length=100)
    message = models.TextField()
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name + ' - ' + self.designation
    
class PaymentDetail(models.Model):
    image = models.FileField(upload_to='payment_images')


