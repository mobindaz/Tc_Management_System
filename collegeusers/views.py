from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models.signals import post_save
from adminuser.models import CustomUser
from django.utils.timezone import now
from student.models import TCApplication , UploadedDueList
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from .forms import ProfileEditForm
from datetime import timedelta
from .models import AutoApprovalSettings
from clerks.models import ClerkAction
import csv
import logging
import threading

logger = logging.getLogger(__name__)


# Process Applications
def process_applications(user):
    """
    Function to process TC applications for a specific user every 2 minutes.
    - If a PRN matches the uploaded due list, the application goes to 'due'.
    - If not, the application is auto-approved.
    """
    # Get all applications in 'pending' status that are at least 2 minutes old
    two_minutes_ago = now() - timedelta(minutes=2)
    pending_apps = TCApplication.objects.filter(status='pending', created_at__lte=two_minutes_ago)

    for app in pending_apps:
        # Check if the PRN exists in any uploaded due list for the given user
        matching_due = UploadedDueList.objects.filter(prn=app.prn, added_by=user)

        if matching_due.exists():
            # Move the application to the due list
            app.status = 'due'
            app.due_users.add(user)
        else:
            # Approve the application
            app.status = 'approved'

        app.save()

# Auto Approval View
@login_required
def auto_approve_view(request):
    """
    View to start the auto-approval process for non-student roles.
    """
    user = request.user

    # Ensure only non-student roles can start auto-approval
    if user.role == 'student':
        return JsonResponse({'error': 'Students are not authorized to access this feature.'}, status=403)

    def auto_approval_task():
        """
        Background task for processing applications every 2 minutes for the current user.
        """
        while True:
            process_applications(user)
            threading.Event().wait(120)  # Wait for 2 minutes before the next execution

    # Run the background task in a new thread
    thread = threading.Thread(target=auto_approval_task, daemon=True)
    thread.start()

    return JsonResponse({'message': f'Auto-approval started successfully for {user.role}.'}, status=200)

@login_required
def auto_approval_settings(request):
    """
    A page to toggle auto-approval on or off.
    """
    user = request.user

    # Ensure only non-student users can toggle the setting
    if user.role == 'student':
        return JsonResponse({'error': 'Students are not authorized to access this feature.'}, status=403)

    # Fetch or create the setting for the current user
    setting, _ = AutoApprovalSettings.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Toggle the auto-approval setting
        auto_approval_state = request.POST.get('auto_approval_state') == 'on'
        setting.auto_approval_enabled = auto_approval_state
        setting.save()

        return JsonResponse({
            'message': f"Auto-approval has been {'enabled' if auto_approval_state else 'disabled'}."
        })

    return render(request, 'auto_approval_settings.html', {'auto_approval_enabled': setting.auto_approval_enabled})

@login_required
def upload_due_list(request):
    """
    Handles the uploading of a due list as a CSV file and displays the list of uploaded dues.
    """
    if request.method == "POST" and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        try:
            # Decode and read the CSV file
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                # Extract fields from the CSV row
                name = row.get('Name', '').strip()
                department = row.get('Department', '').strip()
                prn = row.get('PRN', '').strip()
                due_reason = row.get('Due Reason', 'No reason provided').strip()

                # Validate required fields
                if name and department and prn:
                    UploadedDueList.objects.update_or_create(
                        prn=prn,
                        defaults={
                            'name': name,
                            'department': department,
                            'due_reason': due_reason,
                            'added_by': request.user,
                        },
                    )
            logger.info("CSV file uploaded and processed successfully.")
        except Exception as e:
            logger.error(f"Error processing CSV file: {e}")
            return render(request, 'upload_due_list.html', {'error': "Invalid CSV file format."})

        # Redirect to reload the page
        return HttpResponseRedirect(reverse('upload_due_list'))

    # Fetch uploaded dues only for the logged-in user
    uploaded_due_list = UploadedDueList.objects.filter(added_by=request.user)
    return render(request, 'upload_due_list.html', {'uploaded_due_list': uploaded_due_list})

@login_required
def view_profile(request):
    """View for displaying the user profile."""
    return render(request, 'collegeusers/view_profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    """View for editing the user profile."""
    user = request.user

    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('view_profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileEditForm(instance=user)

    return render(request, 'collegeusers/edit_profile.html', {'form': form})

#@login_required
def hod_dashboard(request):
    # Check if the user is an HOD
    if request.user.role != 'hod':
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Fetch pending and approved applications for the HOD
    pending_applications = TCApplication.objects.filter(status='pending', pending_approval=request.user)
    approved_applications = TCApplication.objects.filter(approved_by=request.user)


    # Pass the data to the template
    context = {
        'pending_applications': pending_applications,
        'approved_applications': approved_applications,
        'role': 'HOD',
    }

    return render(request, 'hod/hod_dashboard.html', context)


@login_required
def lab_dashboard(request):
    if request.user.role != 'lab':
        return HttpResponseForbidden("You are not authorized to access this page.")

    pending_applications = TCApplication.objects.filter(status='pending', pending_approval=request.user)
    approved_applications = TCApplication.objects.filter(approved_by=request.user)

    context = {
        'pending_applications': pending_applications,
        'approved_applications': approved_applications,
        'role': 'lab',
    }
    return render(request, 'science_lab/science_lab_dashboard.html', context)

@login_required
def hostel_dashboard(request):
    if request.user.role != 'hostel':
        return HttpResponseForbidden("You are not authorized to access this page.")

    pending_applications = TCApplication.objects.filter(status='pending', pending_approval=request.user)
    approved_applications = TCApplication.objects.filter(approved_by=request.user)

    context = {
        'pending_applications': pending_applications,
        'approved_applications': approved_applications,
        'role': 'hostel',
    }
    return render(request, 'hostel/hostel_dashboard.html', context)

@login_required
def library_dashboard(request):
    if request.user.role != 'library':
        return HttpResponseForbidden("You are not authorized to access this page.")

    pending_applications = TCApplication.objects.filter(status='pending', pending_approval=request.user)
    approved_applications = TCApplication.objects.filter(approved_by=request.user)

    context = {
        'pending_applications': pending_applications,
        'approved_applications': approved_applications,
        'role': 'library',
    }
    return render(request, 'library/library_dashboard.html', context)


@login_required
def academics_dashboard(request):
    if request.user.role != 'academics':
        return HttpResponseForbidden("You are not authorized to access this page.")

    pending_applications = TCApplication.objects.filter(status='pending', pending_approval=request.user)
    approved_applications = TCApplication.objects.filter(approved_by=request.user)

    context = {
        'pending_applications': pending_applications,
        'approved_applications': approved_applications,
        'role': 'academics',
    }
    return render(request, 'academics/academics_dashboard.html', context)



@login_required
def staff_dashboard(request):
    if request.user.role != 'staff':
        return HttpResponseForbidden("You are not authorized to access this page.")

    pending_applications = TCApplication.objects.filter(status='pending', pending_approval=request.user)
    approved_applications = TCApplication.objects.filter(approved_by=request.user)

    context = {
        'pending_applications': pending_applications,
        'approved_applications': approved_applications,
        'role': 'Staff',
    }
    return render(request, 'staff/staff_dashboard.html', context)


@login_required
def tutor_dashboard(request):
    if request.user.role != 'tutor':
        return HttpResponseForbidden("You are not authorized to access this page.")

    pending_applications = TCApplication.objects.filter(status='pending', pending_approval=request.user)
    approved_applications = TCApplication.objects.filter(approved_by=request.user)

    context = {
        'pending_applications': pending_applications,
        'approved_applications': approved_applications,
        'role': 'Tutor',
    }
    return render(request, 'tutor/tutor_dashboard.html', context)


@login_required
def ncc_dashboard(request):
    if request.user.role != 'ncc':
        return HttpResponseForbidden("You are not authorized to access this page.")

    pending_applications = TCApplication.objects.filter(status='pending', pending_approval=request.user)
    approved_applications = TCApplication.objects.filter(approved_by=request.user)

    context = {
        'pending_applications': pending_applications,
        'approved_applications': approved_applications,
        'role': 'NCC',
    }
    return render(request, 'ncc/ncc_dashboard.html', context)


@login_required
def nss_dashboard(request):
    if request.user.role != 'nss':
        return HttpResponseForbidden("You are not authorized to access this page.")

    pending_applications = TCApplication.objects.filter(status='pending', pending_approval=request.user)
    approved_applications = TCApplication.objects.filter(approved_by=request.user)

    context = {
        'pending_applications': pending_applications,
        'approved_applications': approved_applications,
        'role': 'NSS',
    }
    return render(request, 'nss/nss_dashboard.html', context)


@login_required
def handle_tc_application(request, application_id, action):
    if request.user.role not in ['admin','hod', 'staff', 'tutor', 'ncc', 'nss', 'lab', 'hostel', 'library', 'academics']:
        return HttpResponseForbidden("You are not authorized to perform this action.")

    application = get_object_or_404(TCApplication, id=application_id)

    if action == 'approve':
        application.approve(request.user)
    elif action == 'reject':
        application.status = 'rejected'
    elif action == 'due':
        application.status = 'due'
        application.due_reason = request.POST.get('due_reason', 'No reason provided.')

    application.save()
    return redirect(f'{request.user.role}_dashboard')



@login_required
def forward_to_clerk(request, application_id):
    if request.user.role != 'hod':
        return HttpResponseForbidden("You are not authorized to perform this action.")

    application = get_object_or_404(TCApplication, id=application_id)

    if not application.forwarded_to_clerk:
        # Set the 'forwarded_by' field to the current HOD
        application.forwarded_by = request.user  # Assuming 'forwarded_by' is a ForeignKey to CustomUser
        application.forwarded_to_clerk = True
        application.save()

        # Create a ClerkAction for the forwarded application
        clerk = CustomUser.objects.get(role='clerks')  # Update logic for assigning the correct clerk
        ClerkAction.objects.create(
            clerk=clerk,  # This should be the correct clerk
            tc_application=application
        )

        messages.success(request, "Application forwarded to Clerk.")
    else:
        messages.warning(request, "Application is already forwarded.")

    return redirect('hod_dashboard')



@login_required
def approved_list_view(request, role):
    if request.user.role != role:
        return HttpResponseForbidden("You are not authorized to access this page.")

    approved_applications = TCApplication.objects.filter(approved_by=request.user).prefetch_related('clerk_actions')

    # Handle forward to clerk action
    if request.method == 'POST' and 'forward_to_clerk' in request.POST:
        application_id = request.POST.get('application_id')
        clerk_id = request.POST.get('clerk_id')
        try:
            application = TCApplication.objects.get(id=application_id)
            clerk = CustomUser.objects.get(id=clerk_id, role='clerk')

            # Check if already forwarded
            if ClerkAction.objects.filter(tc_application=application, clerk=clerk).exists():
                messages.warning(request, "This application is already forwarded to the clerk.")
            else:
                ClerkAction.objects.create(tc_application=application, clerk=clerk)
                messages.success(request, "Application forwarded to clerk.")
        except (TCApplication.DoesNotExist, CustomUser.DoesNotExist):
            messages.error(request, "Error forwarding application.")

    clerks = CustomUser.objects.filter(role='clerk')
    context = {
        'approved_applications': approved_applications,
        'role': role.capitalize(),
        'clerks': clerks,
    }
    return render(request, 'approved_list.html', context)



@login_required
def pending_applications(request, role=None):
    user = request.user

    if user.role == 'student':
        pending_list = TCApplication.objects.filter(prn=user.prn, status='pending')
    else:
        pending_list = TCApplication.objects.filter(pending_approval=user)

    return render(request, 'pending_applications.html', {'pending_list': pending_list})



@login_required
def approve_tc(request, tc_id):
    """
    Approve a TC application for the current user.
    The application remains in the pending list for other users until they also approve it.
    """
    application = get_object_or_404(TCApplication, id=tc_id)

    # Check if the current user is in the pending approval list
    if request.user in application.pending_approval.all():
        # Add the current user to the approved list
        application.approved_by.add(request.user)

        # Remove the current user from the pending approval list
        application.pending_approval.remove(request.user)

        # Check if there are no more users left in the pending list
        if not application.pending_approval.exists():
            application.status = 'approved'  # Fully approved only when all users approve

        application.save()
        messages.success(request, f"Application {application.id} approved successfully.")
    else:
        messages.error(request, "You are not authorized to approve this application or have already acted on it.")

    return redirect('pending_applications')

@login_required
def reject_tc(request, tc_id):
    """
    Reject a TC application for the current user.
    """
    application = get_object_or_404(TCApplication, id=tc_id)

    if request.user in application.pending_approval.all():
        application.rejected_by.add(request.user)
        application.pending_approval.remove(request.user)
        application.status = 'rejected'
        application.save()
        messages.success(request, "Application rejected successfully.")
    else:
        messages.error(request, "You are not authorized to reject this application.")

    return redirect('pending_applications')

@login_required
def mark_as_due(request, tc_id):
    """
    Mark a TC application as due for the current user.
    """
    application = get_object_or_404(TCApplication, id=tc_id)

    if request.user in application.pending_approval.all():
        application.due_list.add(request.user)
        application.pending_approval.remove(request.user)
        application.status = 'due'
        application.due_users.add(request.user)
        application.due_reason = request.POST.get('due_reason', 'Due reason not provided')
        application.save()
        messages.success(request, "Application marked as due successfully.")
    else:
        messages.error(request, "You are not authorized to mark this application as due.")

    # Redirect to the pending applications page for the user's role
    user_role = None

    if hasattr(request.user, 'hod'):  # If the user is an HOD
        user_role = 'hod'
    elif hasattr(request.user, 'tutor'):  # If the user is a Tutor
        user_role = 'tutor'
    elif hasattr(request.user, 'staff'):  # If the user is a Staff
        user_role = 'staff'
    elif hasattr(request.user, 'nss'):
        user_role = 'nss'
    elif hasattr(request.user, 'ncc'):
        user_role = 'ncc'
    elif hasattr(request.user, 'lab'):
        user_role = 'lab'
    elif hasattr(request.user, 'hostel'):
        user_role = 'hostel'
    elif hasattr(request.user, 'library'):
        user_role = 'library'
    elif hasattr(request.user, 'academics'):
        user_role = 'academics'    

    return redirect('pending_applications', role=user_role)



@login_required
def remove_due(request, due_id):
    # Fetch the due entry
    due = get_object_or_404(UploadedDueList, id=due_id, added_by=request.user)

    # Delete the entry
    due.delete()

    # Add a success message
    messages.success(request, "The due has been removed successfully.")

    # Redirect back to the due list page
    return HttpResponseRedirect(reverse('upload_due_list'))



@login_required
def due_list(request):
    user = request.user

    # Query manually added due list
    manual_due_list = TCApplication.objects.filter(due_list=user, is_uploaded_due=False)

    # Query uploaded due list
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

@login_required
def approve_due_application(request, application_id):
    """
    Approve a due application and remove it from the due list, moving it to the approved list.
    """
    application = get_object_or_404(TCApplication, id=application_id)

    # Check if the current user is in the due list
    if request.user in application.due_list.all():
        # Remove the user from the due list
        application.due_list.remove(request.user)

        # Add the user to the approved list
        application.approved_by.add(request.user)

        # Update the status if there are no more due users
        if not application.due_list.exists():
            if not application.pending_approval.exists():
                application.status = 'approved'  # Fully approved if no pending approvals
            else:
                application.status = 'pending'  # Still pending approvals from other users

        application.save()

        messages.success(request, f"Application {application.id} approved successfully.")
    else:
        messages.error(request, "You do not have permission to approve this application or it has already been approved.")

    return redirect('due_list')  # Replace with the correct due list URL name




@login_required
def reject_due_application(request, application_id):
    """
    Reject a due application and remove it from the due list.
    """
    application = get_object_or_404(TCApplication, id=application_id)

    # Check if the logged-in user is not a student and is in the due_users list
    if request.user.role == 'student':
        return HttpResponseForbidden("Students cannot reject TC applications.")
    
    if not application.due_users.filter(id=request.user.id).exists():
        return HttpResponseForbidden("You do not have permission to reject this application.")

    if request.method == 'POST':
        # Remove the user from due list and don't add to approved list
        application.due_users.remove(request.user)  # Remove from due list
        application.save()
        return redirect('due_list')  # Redirect back to due list or other page
