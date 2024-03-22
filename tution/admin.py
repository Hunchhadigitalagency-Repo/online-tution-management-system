from django.contrib import admin
from .models import UserProfile,ClassModel,EnrolledStudent,ClassroomResource,EnrollmentPayment
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Count
from django import forms
from ckeditor.widgets import CKEditorWidget

admin.site.unregister(User) # Necessary

class UserProfileInline(admin.TabularInline):
    model = UserProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_user_role')

    def get_user_role(self, obj):
        return obj.userprofile.role if hasattr(obj, 'userprofile') else None

    get_user_role.short_description = 'Role'
    get_user_role.admin_order_field = 'userprofile__role'
    get_user_role.empty_value_display = '-'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('userprofile')
        return queryset

class EnrolledStudentInline(admin.TabularInline):
    model = EnrolledStudent
    extra = 0

class EnrollmentPaymentInline(admin.TabularInline):  # or admin.StackedInline
    model = EnrollmentPayment
    extra = 0  # Number of extra inline forms to display

class EnrolledStudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'class_enrolled', 'status')
    inlines = [EnrollmentPaymentInline]

admin.site.register(EnrolledStudent, EnrolledStudentAdmin)

class ClassModelForm(forms.ModelForm):
    class Meta:
        model = ClassModel
        fields = '__all__'
        widgets = {
            'syllabus': CKEditorWidget(),
        }

class ClassroomResourceInline(admin.TabularInline):
    model = ClassroomResource
    extra = 1
    readonly_fields = ('posted_by',)
    
    
@admin.register(ClassModel)
class ClassModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'teacher', 'get_enrolled_students_count')
    inlines = [EnrolledStudentInline, ClassroomResourceInline]
    form = ClassModelForm

    def get_enrolled_students_count(self, obj):
        return obj.enrolled_students_count

    get_enrolled_students_count.short_description = 'Enrolled Students'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            enrolled_students_count=Count('enrolled_students')
        )
        return queryset