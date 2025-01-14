from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ClerkAction
from django.http import HttpResponseForbidden

@login_required
def clerk_dashboard(request):
    if request.user.role != 'clerks':
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Count pending and approved actions for the logged-in clerk
    pending_count = ClerkAction.objects.filter(clerk=request.user, status='pending').count()
    approved_count = ClerkAction.objects.filter(clerk=request.user, status='approved').count()

    context = {
        'pending_count': pending_count,
        'approved_count': approved_count,
    }
    return render(request, 'clerks/clerk_dashboard.html', context)


@login_required
def pending_list(request):
    if request.user.role != 'clerks':  # Ensure the role is 'clerk', not 'clerks'
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Fetch pending actions with 'forwarded_by' information
    pending_actions = ClerkAction.objects.filter(
        clerk=request.user,
        status='pending'
    ).select_related('tc_application__forwarded_by')  # Select the related 'forwarded_by' data

    if request.method == 'POST':
        action_id = request.POST.get('action_id')
        status = request.POST.get('status')
        reason = request.POST.get('reason', '')  # Default to empty string if not provided

        # Validate the status before updating the action
        if status not in ['approved', 'rejected', 'due']:
            messages.error(request, "Invalid action status.")
            return render(request, 'clerks/pending_list.html', {'pending_actions': pending_actions})

        # Fetch the ClerkAction instance
        action = get_object_or_404(ClerkAction, id=action_id, clerk=request.user)

        # Update the action status and reason
        action.status = status
        action.reason = reason
        action.save()

        # Display success message based on the action
        messages.success(request, f"Application {status.capitalize()} successfully.")

    context = {
        'pending_actions': pending_actions,
    }
    return render(request, 'clerks/pending_list.html', context)




@login_required
def approved_list_clerk(request):
    if request.user.role != 'clerks':
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Fetch approved actions with forwarded_by information
    approved_actions = ClerkAction.objects.filter(
        clerk=request.user, 
        status='approved'
    ).select_related('tc_application__forwarded_by')

    return render(request, 'clerks/approved_list.html', {'approved_actions': approved_actions})


@login_required
def rejected_list_clerk(request):
    if request.user.role != 'clerks':
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Fetch rejected actions with forwarded_by information
    rejected_actions = ClerkAction.objects.filter(
        clerk=request.user, 
        status='rejected'
    ).select_related('tc_application__forwarded_by')

    return render(request, 'clerks/rejected_list.html', {'rejected_actions': rejected_actions})


@login_required
def due_list_clerk(request):
    if request.user.role != 'clerks':
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Fetch due actions with forwarded_by information
    due_actions = ClerkAction.objects.filter(
        clerk=request.user, 
        status='due'
    ).select_related('tc_application__forwarded_by')

    if request.method == 'POST':
        action_id = request.POST.get('action_id')
        status = request.POST.get('status')
        action = get_object_or_404(ClerkAction, id=action_id, clerk=request.user)

        if status in ['approved', 'rejected']:
            action.status = status
            action.save()
            messages.success(request, f"Action {status.capitalize()} successfully.")

    return render(request, 'clerks/due_list.html', {'due_actions': due_actions})
