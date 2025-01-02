from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from student.models import TCApplication
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
import csv

# Dashboard for individual roles
@login_required
def hod_dashboard(request):
    if request.user.role != 'hod':
        return HttpResponseForbidden("You are not authorized to access this page.")

    pending_applications = TCApplication.objects.filter(status='pending', pending_approval=request.user)
    approved_applications = TCApplication.objects.filter(approved_by=request.user)

    context = {
        'pending_applications': pending_applications,
        'approved_applications': approved_applications,
        'role': 'HOD',
    }
    return render(request, 'hod/hod_dashboard.html', context)


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
    if request.user.role not in ['hod', 'staff', 'tutor', 'ncc', 'nss']:
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
def approved_list_view(request, role):
    if request.user.role != role:
        return HttpResponseForbidden("You are not authorized to access this page.")

    approved_applications = TCApplication.objects.filter(approved_by=request.user)

    context = {
        'approved_applications': approved_applications,
        'role': role.capitalize(),
    }
    return render(request, 'approved_list.html', context)

@login_required
def pending_applications(request, role=None):
    """
    Display pending applications for the logged-in user.
    Each user sees applications where they are in the pending approval list.
    """
    user = request.user
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

    return redirect('pending_applications', role=user_role)

@login_required
def upload_due_list(request):
    if request.method == "POST" and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        for row in reader:
            prn = row.get('PRN')
            due_reason = row.get('Due Reason', 'No reason provided')

            try:
                application = TCApplication.objects.get(prn=prn)
                application.add_to_due_list(request.user, due_reason=due_reason, is_uploaded_due=True)
            except TCApplication.DoesNotExist:
                # Handle case where application doesn't exist
                continue

        return HttpResponseRedirect(reverse('due_list'))

    return render(request, 'upload_due_list.html')

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
