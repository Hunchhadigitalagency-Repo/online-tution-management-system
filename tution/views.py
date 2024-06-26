from django.shortcuts import render
from .models import ClassModel,EnrolledStudent,ClassroomResource,EnrollmentPayment,UserProfile,Testimonial,PaymentDetail
from django.contrib.auth import logout,authenticate,login
from django.shortcuts import redirect,get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import IntegrityError

# Create your views here.
def index(request):
    teachers = UserProfile.objects.select_related('user').filter(role='teacher')
    testimonials = Testimonial.objects.all()

    # Count the number of teachers
    teacher_count = UserProfile.objects.filter(role='teacher').count()

    # Count the number of resources
    resource_count = ClassroomResource.objects.count()

     # Count the number of classes
    class_count = ClassModel.objects.count()

    # Count the number of enrolled students
    enrolled_students_count = EnrolledStudent.objects.values('student').distinct().count()
    return render(request, 'main.html', {'teachers': teachers,'testimonials':testimonials,'teacher_count':teacher_count,'class_count': class_count, 'resource_count': resource_count,'enrolled_students_count': enrolled_students_count}) 

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
        return redirect('/login/') 

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
                    login(request, request.user)
                    messages.success(request, "Password changed successfully.")
                    if is_teacher:
                        return render(request,'teacher/profile.html') 
                    else:
                        return render(request,'user/profile.html')
                else:
                    if is_teacher:
                        messages.error(request, "Confirm password didnt match with new password.")
                        return render(request,'teacher/profile.html',{'confirm_password_error': True}) 
                    else:
                        return render(request,'user/profile.html')
            else:
                if is_teacher:
                    messages.error(request, "Old password didnt match.")
                    return render(request,'teacher/profile.html', {'old_password_error': True}) 
                else:
                    return render(request,'user/profile.html')
        elif (old_password and not new_password) or (old_password and not confirm_password):
            if is_teacher:
                return render(request,'teacher/profile.html') 
            else:
                return render(request,'user/profile.html')
        elif (new_password or confirm_password) and not old_password:
            if is_teacher:
                return render(request,'teacher/profile.html') 
            else:
                return render(request,'user/profile.html')
    
    if is_teacher:
        return render(request,'teacher/profile.html') 
    else:
        return render(request,'user/profile.html')

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

    payment = PaymentDetail.objects.first()


    # Check if the user and class are already enrolled
    existing_enrollment = EnrolledStudent.objects.filter(student=request.user, class_enrolled__id=class_id).first()
    if existing_enrollment:

        # If enrollment exists, return that data
        return render(request, "user/paymentPage.html", {'enroll_data': existing_enrollment,'payment_details':payment})
    
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



    return render(request,"user/paymentPage.html",{'enroll_data':enrolled_class,'payment_details':payment})

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
    payment = PaymentDetail.objects.first()
    print(f"payment ho yo {payment}")
    return render(request,"user/paymentPage.html",{'payment_details':payment})

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

        # Attempt authentication using the provided username
        user = authenticate(request, username=username, password=password)

        # If authentication fails with username, attempt with email
        if user is None:
            # Check if there is a user with the provided email
            try:
                user_with_email = User.objects.get(email=username)
                user = authenticate(request, username=user_with_email.username, password=password)
            except User.DoesNotExist:
                pass

        # If user is authenticated, log them in
        if user is not None:
            login(request, user)
            # Redirect to a success page or home page
            return redirect('/dashboard/')  # Replace 'dashboard' with the name of your dashboard URL pattern
        else:
            # Return an error message if authentication fails
            error = 'Invalid username or password.'
            return render(request, 'auth/login.html', {'error': error})
    else:
        return render(request, 'auth/login.html')

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Initialize an empty dictionary for errors
        errors = {}
        
        # Check if any field is empty
        if not email:
            errors['email'] = "Email field is required."
        if not username:
            errors['username'] = "Username field is required."
        if not password:
            errors['password'] = "Password field is required."
        if not confirm_password:
            errors['confirm_password'] = "Confirm Password field is required."
        
        # Check if passwords match
        if password != confirm_password:
            errors['password_match'] = "Passwords do not match"
        
        # Check if email or username already exist
        existing_user = User.objects.filter(username=username).exists()
        if existing_user:
            errors['username'] = f"Username '{username}' is already taken."
        existing_email = User.objects.filter(email=email).exists()
        if existing_email:
            errors['email'] = f"Email '{email}' is already registered."
        
        if errors:
            # If there are errors, return to the register page with error messages
            return render(request, 'auth/register.html', {'errors': errors, 'email': email, 'username': username})
        
        try:
            # Create User instance
            user = User.objects.create_user(username=username, email=email, password=password)
            
            # Create UserProfile instance
            UserProfile.objects.create(user=user, role='student')
            
            # Redirect to a success page or login page
            messages.success(request, "Youre now registered student")
            return redirect('/login/')  # Adjust this to your login URL
        except IntegrityError as e:
            if 'UNIQUE constraint failed: auth_user.username' in str(e):
                errors['username'] = f"Username '{username}' is already taken."
            else:
                errors['unknown_error'] = "An error occurred. Please try again."
            
            return render(request, 'auth/register.html', {'errors': errors, 'email': email, 'username': username})
    else:
        return render(request, 'auth/register.html')

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
