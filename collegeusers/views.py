from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models.signals import post_save
from adminuser.models import CustomUser
from django.utils.timezone import now
from student.models import TCApplication, UploadedDueList
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
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
    two_minutes_ago = now() - timedelta(minutes=2)
    pending_apps = TCApplication.objects.filter(status='pending', created_at__lte=two_minutes_ago)

    for app in pending_apps:
        matching_due = UploadedDueList.objects.filter(prn=app.prn, added_by=user)

        if matching_due.exists():
            app.status = 'due'
            app.due_users.add(user)
        else:
            app.status = 'approved'

        app.save()

# Auto Approval View
@login_required
def auto_approve_view(request):
    user = request.user

    if user.role == 'student':
        return JsonResponse({'error': 'Students are not authorized to access this feature.'}, status=403)

    def auto_approval_task():
        while True:
            process_applications(user)
            threading.Event().wait(120)

    thread = threading.Thread(target=auto_approval_task, daemon=True)
    thread.start()

    return JsonResponse({'message': f'Auto-approval started successfully for {user.role}.'}, status=200)

@login_required
def auto_approval_settings(request):
    user = request.user

    if user.role == 'student':
        return JsonResponse({'error': 'Students are not authorized to access this feature.'}, status=403)

    setting, _ = AutoApprovalSettings.objects.get_or_create(user=user)

    if request.method == 'POST':
        auto_approval_state = request.POST.get('auto_approval_state') == 'on'
        setting.auto_approval_enabled = auto_approval_state
        setting.save()

        return JsonResponse({
            'message': f"Auto-approval has been {'enabled' if auto_approval_state else 'disabled'}."
        })

    return render(request, 'auto_approval_settings.html', {'auto_approval_enabled': setting.auto_approval_enabled})

@login_required
def upload_due_list(request):
    if request.method == "POST" and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                name = row.get('Name', '').strip()
                department = row.get('Department', '').strip()
                prn = row.get('PRN', '').strip()
                due_reason = row.get('Due Reason', 'No reason provided').strip()

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
        except Exception as e:
            logger.error(f"Error processing CSV file: {e}")
            return render(request, 'upload_due_list.html', {'error': "Invalid CSV file format."})

        return HttpResponseRedirect(reverse('upload_due_list'))

    uploaded_due_list = UploadedDueList.objects.filter(added_by=request.user)
    return render(request, 'upload_due_list.html', {'uploaded_due_list': uploaded_due_list})

@login_required
def view_profile(request):
    return render(request, 'collegeusers/view_profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    user = request.user

    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('view_profile')
    else:
        form = ProfileEditForm(instance=user)

    return render(request, 'collegeusers/edit_profile.html', {'form': form})

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
    return render(request, 'academic_sessions/academic_sessions_dashboard.html', context)

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
        application.forwarded_by = request.user
        application.forwarded_to_clerk = True
        application.save()

        clerk = CustomUser.objects.get(role='clerks')
        ClerkAction.objects.create(
            clerk=clerk,
            tc_application=application
        )

    return redirect('hod_dashboard')

@login_required
def bulk_forward_to_clerk(request):
    if request.user.role != 'hod':
        return HttpResponseForbidden("You are not authorized to perform this action.")

    selected_ids = request.POST.getlist('selected_applications')

    if not selected_ids:
        return redirect(reverse('approved_list', kwargs={'role': 'hod'}))

    applications = TCApplication.objects.filter(id__in=selected_ids)

    for application in applications:
        if not application.forwarded_to_clerk:
            application.forwarded_by = request.user
            application.forwarded_to_clerk = True
            application.save()

            clerk = CustomUser.objects.get(role='clerks')
            ClerkAction.objects.create(clerk=clerk, tc_application=application)

    return redirect(reverse('approved_list', kwargs={'role': 'hod'}))

@login_required
def approved_list_view(request, role):
    if request.user.role != role:
        return HttpResponseForbidden("You are not authorized to access this page.")

    approved_applications = TCApplication.objects.filter(approved_by=request.user).prefetch_related('clerk_actions')

    if request.method == 'POST' and 'forward_to_clerk' in request.POST:
        application_id = request.POST.get('application_id')
        clerk_id = request.POST.get('clerk_id')
        try:
            application = TCApplication.objects.get(id=application_id)
            clerk = CustomUser.objects.get(id=clerk_id, role='clerk')

            if not ClerkAction.objects.filter(tc_application=application, clerk=clerk).exists():
                ClerkAction.objects.create(tc_application=application, clerk=clerk)
        except (TCApplication.DoesNotExist, CustomUser.DoesNotExist):
            pass

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
    application = get_object_or_404(TCApplication, id=tc_id)

    if request.user in application.pending_approval.all():
        application.approved_by.add(request.user)
        application.pending_approval.remove(request.user)

        if not application.pending_approval.exists():
            application.status = 'approved'

        application.save()
    return redirect('pending_applications')

@login_required
def reject_tc(request, tc_id):
    application = get_object_or_404(TCApplication, id=tc_id)

    if request.user in application.pending_approval.all():
        application.rejected_by.add(request.user)
        application.pending_approval.remove(request.user)
        application.status = 'rejected'
        application.save()
    return redirect('pending_applications')

@login_required
def mark_as_due(request, tc_id):
    application = get_object_or_404(TCApplication, id=tc_id)

    if request.user in application.pending_approval.all():
        application.due_list.add(request.user)
        application.pending_approval.remove(request.user)
        application.status = 'due'
        application.due_users.add(request.user)
        application.due_reason = request.POST.get('due_reason', 'Due reason not provided')
        application.save()

    user_role = None

    if hasattr(request.user, 'hod'):
        user_role = 'hod'
    elif hasattr(request.user, 'tutor'):
        user_role = 'tutor'
    elif hasattr(request.user, 'staff'):
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
    due = get_object_or_404(UploadedDueList, id=due_id, added_by=request.user)
    due.delete()
    return HttpResponseRedirect(reverse('upload_due_list'))

@login_required
def due_list(request):
    user = request.user

    manual_due_list = TCApplication.objects.filter(due_list=user, is_uploaded_due=False)
    uploaded_due_list = TCApplication.objects.filter(due_list=user, is_uploaded_due=True)

    context = {
        'manual_due_list': manual_due_list,
        'uploaded_due_list': uploaded_due_list,
    }

    return render(request, 'due_list.html', context)

@login_required
def approve_due_application(request, application_id):
    application = get_object_or_404(TCApplication, id=application_id)

    if request.user in application.due_list.all():
        application.due_list.remove(request.user)
        application.approved_by.add(request.user)

        if not application.due_list.exists():
            if not application.pending_approval.exists():
                application.status = 'approved'
            else:
                application.status = 'pending'

        application.save()
    return redirect('due_list')

@login_required
def reject_due_application(request, application_id):
    application = get_object_or_404(TCApplication, id=application_id)

    if request.user.role == 'student':
        return HttpResponseForbidden("Students cannot reject TC applications.")
    
    if not application.due_users.filter(id=request.user.id).exists():
        return HttpResponseForbidden("You do not have permission to reject this application.")

    if request.method == 'POST':
        application.due_users.remove(request.user)
        application.save()
        return redirect('due_list')

@login_required
def bulk_action(request):
    if request.method == "POST":
        action = request.POST.get("action")
        selected_ids = request.POST.getlist("selected_applications")

        if not selected_ids:
            return redirect('pending_applications', role=get_user_role(request.user))

        applications = TCApplication.objects.filter(id__in=selected_ids)

        if action == "approve":
            for app in applications:
                if request.user in app.pending_approval.all():
                    app.approved_by.add(request.user)
                    app.pending_approval.remove(request.user)
                    if not app.pending_approval.exists():
                        app.status = 'approved'
                    app.save()

        elif action == "reject":
            for app in applications:
                if request.user in app.pending_approval.all():
                    app.rejected_by.add(request.user)
                    app.pending_approval.remove(request.user)
                    app.status = 'rejected'
                    app.save()

        elif action == "due":
            for app in applications:
                if request.user in app.pending_approval.all():
                    app.due_list.add(request.user)
                    app.pending_approval.remove(request.user)
                    app.status = 'due'
                    app.save()

    return redirect('pending_applications', role=get_user_role(request.user))

def get_user_role(user):
    if hasattr(user, 'hod'):
        return 'hod'
    elif hasattr(user, 'tutor'):
        return 'tutor'
    elif hasattr(user, 'staff'):
        return 'staff'
    elif hasattr(user, 'nss'):
        return 'nss'
    elif hasattr(user, 'ncc'):
        return 'ncc'
    elif hasattr(user, 'lab'):
        return 'lab'
    elif hasattr(user, 'hostel'):
        return 'hostel'
    elif hasattr(user, 'library'):
        return 'library'
    elif hasattr(user, 'academics'):
        return 'academics'
    return None
