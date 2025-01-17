from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db import IntegrityError
from student.models import TCApplication, UploadedDueList  # Adjust import path as needed
from django.contrib.auth import get_user_model
from django.shortcuts import  get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
import csv
from django.core.exceptions import ValidationError


CustomUser = get_user_model()


DEPARTMENT_CHOICES = [
        ('CHE', 'COMPUTER HARDWARE ENGINEERING'),
        ('CE', 'CIVIL ENGINEERING'),
        ('ME', 'MECHANICAL ENGINEERING'),
        ('IE', 'INSTRUMENTATION ENGINEERING'),
        ('EE', 'ELECTRONICS ENGINEERING'),
        ('EEE', 'ELECTRICAL AND ELECTRONICS ENGINEERING'),
        ('nss', 'NSS'),
        ('ncc', 'NCC'),
        ('lab', 'Lab'),
        ('hostel', 'Hostel'),
        ('library', 'Library'),
        ('academics', 'Academics'),
        ('clerks', 'Clerks'),
    ]

@login_required
def admin_panel(request):
    """
    View for admin to upload a CSV file and create users with role-specific limitations.
    """
    if request.user.is_superuser or getattr(request.user, 'role', None) == 'admin':
        if request.method == "POST" and request.FILES.get('csv_file'):
            csv_file = request.FILES['csv_file']

            try:
                # Decode the uploaded file and parse CSV rows
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)

                created_users = []
                skipped_users = []

                # Role limits
                max_hods = 6
                max_tutors = 6
                max_ncc = 1
                max_nss = 1

                hod_count = CustomUser.objects.filter(role='hod').count()
                tutor_count = CustomUser.objects.filter(role='tutor').count()
                ncc_count = CustomUser.objects.filter(role='ncc').count()
                nss_count = CustomUser.objects.filter(role='nss').count()

                for row in reader:
                    username = row.get('username', '').strip().lower()
                    raw_password = row.get('password', '').strip()
                    role = row.get('role', '').strip().lower()
                    first_name = row.get('first_name', '').strip().capitalize()
                    last_name = row.get('last_name', '').strip().capitalize()
                    email = row.get('email', '').strip().lower()
                    department = row.get('department', '').strip().upper()  # Use uppercase for department codes
                    prn = row.get('prn', '').strip()

                    # Validate that essential fields are present
                    if not username or not raw_password or not role:
                        skipped_users.append(f"Missing required fields for user: {row}")
                        continue

                    # Check if the user already exists
                    if CustomUser.objects.filter(username=username).exists():
                        skipped_users.append(f"Username '{username}' already exists.")
                        continue

                    # Validate department choice
                    department_choices = dict(DEPARTMENT_CHOICES)
                    if department and department not in department_choices.keys():
                        skipped_users.append(f"Invalid department '{department}' for user: {username}")
                        continue

                    # Validate role-specific limitations
                    if role == 'hod' and hod_count >= max_hods:
                        skipped_users.append(f"Cannot create more than {max_hods} HODs. Skipping {username}.")
                        continue
                    elif role == 'tutor' and tutor_count >= max_tutors:
                        skipped_users.append(f"Cannot create more than {max_tutors} Tutors. Skipping {username}.")
                        continue
                    elif role == 'ncc' and ncc_count >= max_ncc:
                        skipped_users.append(f"Cannot create more than {max_ncc} NCC users. Skipping {username}.")
                        continue
                    elif role == 'nss' and nss_count >= max_nss:
                        skipped_users.append(f"Cannot create more than {max_nss} NSS users. Skipping {username}.")
                        continue

                    # PRN validation: Only check PRN for student users
                    if role == 'student':
                        if not prn:
                            skipped_users.append(f"PRN is mandatory for student: {username}")
                            continue
                        if CustomUser.objects.filter(prn=prn).exists():
                            skipped_users.append(f"User with PRN '{prn}' already exists.")
                            continue
                    else:
                        prn = None  # Ensure PRN is not saved for non-student users

                    try:
                        # Create and save the user
                        user = CustomUser(
                            username=username,
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                            role=role,
                            department=department,
                            prn=prn
                        )
                        user.set_password(raw_password)  # Set password securely
                        user.full_clean()  # Trigger validation
                        user.save()

                        # Update counts based on role
                        if role == 'hod':
                            hod_count += 1
                        elif role == 'tutor':
                            tutor_count += 1
                        elif role == 'ncc':
                            ncc_count += 1
                        elif role == 'nss':
                            nss_count += 1

                        created_users.append(username)

                    except ValidationError as ve:
                        skipped_users.append(f"Validation error for user '{username}': {ve.message_dict}")
                    except IntegrityError as e:
                        skipped_users.append(f"Error creating user '{username}': {str(e)}")

                # Provide feedback to the admin
                if created_users:
                    messages.success(request, f"Successfully created users: {', '.join(created_users)}")
                if skipped_users:
                    messages.error(request, f"Skipped users: {', '.join(skipped_users)}")

            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")

            return redirect('manage_users')

        return render(request, 'adminuser/admin_panel.html')
    else:
        return HttpResponseForbidden("You are not authorized to access the admin panel.")


@login_required
def manage_users(request):
    # Ensure the user is authorized (superuser or admin role)
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'admin'):
        return redirect('admin_panel')

    # Exclude staff members from the user list
    all_users = CustomUser.objects.filter(is_staff=False)

    # Add role determination logic
    for user in all_users:
        if user.is_superuser:
            user.role = "Superuser"
        elif getattr(user, 'role', '') == 'admin':
            user.role = "Admin"
        elif getattr(user, 'role', '') == 'hod':
            user.role = "HOD"
        elif getattr(user, 'role', '') == 'tutor':
            user.role = "Tutor"
        elif getattr(user, 'role', '') == 'ncc':
            user.role = "NCC"
        elif getattr(user, 'role', '') == 'nss':
            user.role = "NSS"
        elif getattr(user, 'role', '') == 'lab':
            user.role = "Lab"
        elif getattr(user, 'role', '') == 'hostel':
            user.role = "Hostel"
        elif getattr(user, 'role', '') == 'library':
            user.role = "Library"
        elif getattr(user, 'role', '') == 'academics':
            user.role = "Academics"
        elif getattr(user, 'role', '') == 'staff':
            user.role = "Staff"
        elif getattr(user, 'role', '') == 'clerks':
            user.role = "Clerks"
        elif getattr(user, 'role', '') == 'student':
            user.role = "Student"
        else:
            user.role = "User"  # Default role if none matches

    context = {
        'all_users': all_users,
    }
    return render(request, 'adminuser/manage_users.html', context)

@login_required
def edit_user(request, user_id):
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'admin'):
        return redirect('admin_panel')

    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.is_staff = 'is_staff' in request.POST
        user.is_active = 'is_active' in request.POST
        user.save()
        return redirect('manage_users')

    context = {'user': user}
    return render(request, 'adminuser/edit_user.html', context)


@login_required
def delete_user(request, user_id):
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'admin'):
        return redirect('admin_panel')

    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        user.delete()
        return redirect('manage_users')

    context = {'user': user}
    return render(request, 'adminuser/delete_user.html', context)        


# @login_required
# def approve_tc_list(request):
#     if request.user.is_superuser or getattr(request.user, 'role', None) in ['admin']:
#         pending_applications = TCApplication.objects.filter(status='pending')
#         return render(request, 'adminuser/approve_tc.html', {'pending_applications': pending_applications})
#     else:
#         return HttpResponseForbidden("You are not authorized to access this page.")

# @login_required
# def approve_tc_action(request, application_id):
#     print(f"User: {request.user.username}, Role: {getattr(request.user, 'role', 'None')}, Superuser: {request.user.is_superuser}")


#     if not request.user.is_superuser and getattr(request.user, 'role', None) != 'adminuser':
#         print("Unauthorized access: User is not a superuser or admin.")
#         return HttpResponseForbidden("You are not authorized to perform this action.")

#     try:
#         application = TCApplication.objects.get(id=application_id)
#         print(f"Fetched Application ID: {application.id}, Current Status: {application.status}")

#         if application.status == 'approved':
#             print(f"Application ID {application_id} is already approved.")
#             return HttpResponseForbidden("This application has already been approved.")


#         application.status = 'approved'

    
#         application.approved_by.add(request.user)  
#         application.save()

#         print(f"Application ID {application.id} successfully approved by {request.user.username}.")
        
        
#         next_page = request.GET.get('next', 'pending_tc_list')
#         return redirect(next_page)

#     except TCApplication.DoesNotExist:
#         print(f"Application ID {application_id} does not exist.")
#         return HttpResponseForbidden("The application does not exist.")


# @login_required
# def reject_tc_action(request, application_id):
#     application = TCApplication.objects.get(id=application_id)
#     application.status = 'rejected'
#     application.save()
#     return redirect('approve_tc_list')


# @login_required
# def approved_tc_list(request):
#     if request.user.is_superuser or getattr(request.user, 'role', None) in ['admin']:
#         approved_applications = TCApplication.objects.filter(status='approved')
#         return render(request, 'adminuser/approved_tc.html', {'approved_applications': approved_applications})
#     else:
#         return HttpResponseForbidden("You are not authorized to access this page.")


# @login_required
# def pending_tc_list(request):
#     if request.user.is_superuser or getattr(request.user, 'role', None) in ['admin']:
#         pending_applications = TCApplication.objects.filter(status='pending')
#         rejected_applications = TCApplication.objects.filter(status='rejected')
#         return render(request, 'adminuser/pending_tc.html', {
#             'pending_applications': pending_applications,
#             'rejected_applications': rejected_applications
#         })
#     else:
#         return HttpResponseForbidden("You are not authorized to access this page.")


# @login_required
# def mark_as_due(request, application_id):
#     application = TCApplication.objects.get(id=application_id)
#     if request.method == 'POST':
#         due_reason = request.POST.get('due_reason', 'Not Completed')
#         try:
            
#             application.status = 'due'
#             application.due_reason = due_reason
#             application.save()
#             return redirect('due_list')  
#         except TCApplication.DoesNotExist:
#             return HttpResponseForbidden("Application does not exist.")


    
#     return render(request, 'adminuser/mark_as_due.html', {
#         'application': application,
#         'due_reasons': ['Fees Due', 'Library Fine', 'Hostel Dues', 'Other'],  
#     })

# @login_required
# def upload_due_list(request):
#     if request.method == "POST" and request.FILES.get('csv_file'):
#         csv_file = request.FILES['csv_file']
#         decoded_file = csv_file.read().decode('utf-8').splitlines()
#         reader = csv.DictReader(decoded_file)

#         for row in reader:
#             name = row.get('Name')  
#             department = row.get('Department')  
#             prn = row.get('PRN') 
#             due_reason = row.get('Due Reason', 'No reason provided')  
        
#             UploadedDueList.objects.update_or_create(
#                 prn=prn,
#                 defaults={
#                     'name': name,
#                     'department': department,
#                     'due_reason': due_reason,
#                     'added_by': request.user,
#                 },
#             )

#         return HttpResponseRedirect(reverse('upload_due_list'))

    
#     uploaded_due_list = UploadedDueList.objects.filter(added_by=request.user)

#     return render(request, 'upload_due_list.html', {'uploaded_due_list': uploaded_due_list})





@login_required
def admin_due_list(request):
    user = request.user

 
    manual_due_list = TCApplication.objects.filter(due_list=user, is_uploaded_due=False)


    uploaded_due_list = TCApplication.objects.filter(due_list=user, is_uploaded_due=True)
    due_applications = TCApplication.objects.filter(due_users=request.user)

    context = {
        'due_applications': due_applications,
    }

    return render(
        request,
        'due_list.html',
        {
            'manual_due_list': manual_due_list,
            'uploaded_due_list': uploaded_due_list,
        }
    )
