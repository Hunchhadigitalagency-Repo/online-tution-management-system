from django.shortcuts import render
from .models import ClassModel,EnrolledStudent,ClassroomResource,EnrollmentPayment,UserProfile,Testimonial
from django.contrib.auth import logout,authenticate,login
from django.shortcuts import redirect,get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
import os   
from django.conf import settings
from django.contrib.auth.hashers import make_password

# Create your views here.
def index(request):
    teachers = UserProfile.objects.select_related('user').filter(role='teacher')
    testimonials = Testimonial.objects.all()
    return render(request, 'main.html', {'teachers': teachers,'testimonials':testimonials}) 

def dashbaord(request):
    if request.user.is_authenticated:
        # Retrieve the current logged-in user
        current_user = request.user
        is_teacher = current_user.userprofile.role == 'teacher' if hasattr(current_user, 'userprofile') else False
        if is_teacher:
            teacher_classes = ClassModel.objects.filter(teacher=current_user)
            return render(request,'teacher/index.html',{'classes': teacher_classes})  
        else:
            # Filter the classes where the current user has been enrolled
            enrolled_classes = ClassModel.objects.filter(enrolled_students__student=current_user)
            return render(request, 'user/index.html', {'classes': enrolled_classes})
    else:
        # Redirect to login page or handle unauthenticated user
        return redirect('login') 

def profile(request):
    current_user = request.user
    is_teacher = current_user.userprofile.role == 'teacher' if hasattr(current_user, 'userprofile') else False
    if request.method == 'POST':
        # Update profile picture
        profile = request.FILES.get('profile')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        if first_name:
            request.user.first_name = first_name
            request.user.save()
            
        if last_name:
            request.user.last_name = last_name
            request.user.save()

        if profile:
            request.user.userprofile.profile = profile
            request.user.userprofile.save()

        # Handle password change
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if old_password and new_password and confirm_password:
            # Check if old password is correct
            user = authenticate(username=request.user.username, password=old_password)
            if user is not None:
                # Check if new password matches confirm password
                if new_password == confirm_password:
                    # Update user's password
                    request.user.password = make_password(new_password)
                    request.user.save()
                    messages.success(request, "Password changed successfully.")
                    if is_teacher:
                        return render(request,'teacher/profile.html') 
                    else:
                        return render(request,'user/profile.html');
                else:
                    if is_teacher:
                        messages.error(request, "Confirm password didnt match with new password.")
                        return render(request,'teacher/profile.html',{'confirm_password_error': True}) 
                    else:
                        return render(request,'user/profile.html');
            else:
                if is_teacher:
                    messages.error(request, "Old password didnt match.")
                    return render(request,'teacher/profile.html', {'old_password_error': True}) 
                else:
                    return render(request,'user/profile.html');
        elif (old_password and not new_password) or (old_password and not confirm_password):
            if is_teacher:
                return render(request,'teacher/profile.html') 
            else:
                return render(request,'user/profile.html');
        elif (new_password or confirm_password) and not old_password:
            if is_teacher:
                return render(request,'teacher/profile.html') 
            else:
                return render(request,'user/profile.html');
    
    if is_teacher:
        return render(request,'teacher/profile.html') 
    else:
        return render(request,'user/profile.html');

def classes(request):
    classes = ClassModel.objects.all()
    return render(request, 'user/classes.html', {'classes': classes})

def classDetails(request,id):
    class_details = ClassModel.objects.get(id=id)
    return render(request,'user/classDetails.html',{'class_details':class_details})

def enrollToClass(request,class_id):
    full_name = request.POST.get('full_name')
    phone_number = request.POST.get('phone_number')
    parent_name = request.POST.get('parent_name')
    parent_phone_number = request.POST.get('parent_phone_number')
    address = request.POST.get('address')

    # Check if the user and class are already enrolled
    existing_enrollment = EnrolledStudent.objects.filter(student=request.user, class_enrolled__id=class_id).first()
    if existing_enrollment:
        # If enrollment exists, return that data
        return render(request, "user/paymentPage.html", {'enroll_data': existing_enrollment})
    
    # Assuming EnrolledClass is the model where you want to store this data
    enrolled_class = EnrolledStudent(
        class_enrolled=ClassModel.objects.get(id=class_id),
        student = request.user,
        full_name=full_name,
        phone_number=phone_number,
        parent_name=parent_name,
        parent_phone_number=parent_phone_number,
        address=address
    )
    enrolled_class.save()

    return render(request,"user/paymentPage.html",{'enroll_data':enrolled_class})

def submitPayment(request,enroll_id):
    if request.method == 'POST':
        payment_proof = request.FILES.get('file')  # Dropzone.js uses 'file' as the default parameter name
        enrollment_id = enroll_id

        if not payment_proof:
            return JsonResponse({'error': 'Payment proof file is required.'}, status=400)
        elif not enrollment_id:
            return JsonResponse({'error': 'Enrollment ID is required.'}, status=400)
        else:
            enrollment = get_object_or_404(EnrolledStudent, id=enrollment_id)
            payment = EnrollmentPayment(enrollment=enrollment, payment_proof=payment_proof)
            payment.save()
            return JsonResponse({'success': True})  # Respond with success status

    return JsonResponse({'error': 'Invalid request.'}, status=400)

def editClassMeetLink(request,class_id):
    class_details = get_object_or_404(ClassModel, id=class_id)

    if request.method == 'POST':
        meet_link = request.POST.get('meet_link')
        class_details.meet_link = meet_link
        class_details.save()
        return redirect(f'/enrolled-classes/{class_id}')  # Redirect to a success page or URL

def paymentPage(request):
    return render(request,"user/paymentPage.html")

def myClasses(request):
    # Retrieve the current logged-in user
    current_user = request.user

    # Filter the classes where the current user has been enrolled
    enrolled_classes = ClassModel.objects.filter(enrolled_students__student=current_user)

    return render(request, 'user/myClasses.html', {'classes': enrolled_classes})

def enrolledClasses(request, id):
    current_user = request.user

    is_teacher = current_user.userprofile.role == 'teacher' if hasattr(current_user, 'userprofile') else False
    if is_teacher:
        # Retrieve class details
        class_details = ClassModel.objects.get(id=id)

        class_resource = ClassroomResource.objects.filter(class_model=class_details).order_by('-id')
        
        return render(request,'teacher/enrolledClasses.html',{'class_details': class_details, 'class_resources':class_resource})
    else:
        # Retrieve class details
        class_details = ClassModel.objects.get(id=id)

        class_resource = ClassroomResource.objects.filter(class_model=class_details).order_by('-id')
        
        # Check current user's enrollment status for the class
        try:
            enrollment_status = EnrolledStudent.objects.get(student=current_user, class_enrolled=class_details).status
            can_attend = True if enrollment_status == 'can_attend' else False
        except EnrolledStudent.DoesNotExist:
            can_attend = False
        
        return render(request, 'user/enrolledClasses.html', {'class_details': class_details, 'can_attend': can_attend,'class_resources':class_resource})


def loginUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page or home page
            return redirect('/dashboard/')  # Replace 'home' with the name of your home URL pattern
        else:
            # Return an error message if authentication fails
            messages.error(request, 'Invalid username or password.')
            return redirect('/login/')  # Redirect back to the login page
    else:
        return render(request, 'auth/login.html')

def register(request):
    return render(request,'auth/register.html')

def logoutUser(request):
    logout(request)
    return redirect('/') 

def postResources(request, class_id):
    if request.method == 'POST':
        resource_file = request.FILES.get('file')
        message = request.POST.get('message')
        class_model = ClassModel.objects.get(id=class_id)
        posted_by = request.user

        # Check if either resource file or message is provided
        if resource_file or message:
            # Create a new ClassroomResource object and save it
            resource = ClassroomResource.objects.create(
                class_model=class_model,
                resource_file=resource_file,
                message=message,
                posted_by=posted_by
            )
            class_details = ClassModel.objects.get(id=class_id)

            class_resource = ClassroomResource.objects.filter(class_model=class_details).order_by('-id')
            
            # Handle the case where neither file nor message is provided
            return render(request, 'teacher/enrolledClasses.html',{'class_details': class_details, 'class_resources':class_resource})
        else:
            class_details = ClassModel.objects.get(id=class_id)

            class_resource = ClassroomResource.objects.filter(class_model=class_details).order_by('-id')
        
            # Handle the case where neither file nor message is provided
            return render(request, 'teacher/enrolledClasses.html',{'class_details': class_details, 'class_resources':class_resource}, {'error_message': 'You must provide either a file or a message.'})

    class_details = ClassModel.objects.get(id=class_id)

    class_resource = ClassroomResource.objects.filter(class_model=class_details).order_by('-id')
    
    # Handle the case where neither file nor message is provided
    return render(request, 'teacher/enrolledClasses.html',{'class_details': class_details, 'class_resources':class_resource})


def update_course_syllabus(request, course_id):
    if request.method == 'POST':
        # Get the course object
        try:
            course = ClassModel.objects.get(id=course_id)
        except ClassModel.DoesNotExist:
            messages.error(request, "Course not found.")
            return redirect(f'/enrolled-classes/{course_id}')  # Redirect to a suitable URL if course doesn't exist

        # Update the syllabus
        syllabus = request.POST.get('syllabus')
        course.syllabus = syllabus
        course.save()

        messages.success(request, "Syllabus updated successfully.")
        return redirect(f'/enrolled-classes/{course_id}')  # Redirect to a suitable URL after successful update
