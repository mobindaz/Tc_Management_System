from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from student.models import TCApplication, UploadedDueList
from django.http import HttpResponseForbidden, FileResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from adminuser.models import CustomUser
from django.db import transaction
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)

from django.db.models import Q

def check_and_process_due_status(prn, application, relevant_users):
    """
    Checks uploaded due lists for the given PRN and processes due entries.

    Parameters:
        prn (str): The PRN of the student.
        application (TCApplication): The TC application object.
        relevant_users (QuerySet): Relevant users (departmental and general) to check due lists.

    Returns:
        bool: True if the application was marked as 'due', False otherwise.
    """
    # Step 1: Fetch all uploaded due list entries for this PRN by relevant users
    due_entries = UploadedDueList.objects.filter(prn=prn, added_by__in=relevant_users)

    if due_entries.exists():
        # Step 2: Add each relevant user to the application's due list
        for entry in due_entries:
            application.due_list.add(entry.added_by)
        
        # Step 3: Delete the uploaded due list entries (bulk action)
        due_entries.delete()

        # Step 4: Update application status to 'due'
        application.status = 'due'
        application.save()

        # Return True to indicate that the application was marked as 'due'
        return True

    # Return False if no due entries were found
    return False

@login_required
def user_dashboard(request):
    """
    Student dashboard to apply for a Transfer Certificate (TC).
    Checks uploaded due lists for relevant users and updates the application's status accordingly.
    """
    if request.user.role != 'student':
        return HttpResponseForbidden("You are not authorized to access the student dashboard.")

    # Fetch the student's existing TC application
    application = TCApplication.objects.filter(prn=request.user.prn).first()

    if application:
        # If an application already exists, redirect to the application status page
        return redirect('application_status')

    if request.method == 'POST':
        # Fetch data from the POST request
        name = request.POST.get('name')
        roll_number = request.POST.get('roll_number')
        department = request.user.department  # Automatically fetch department from the user's profile
        prn = request.user.prn  # Use the logged-in user's PRN
        reason = request.POST.get('reason')

        # Create a new TC application
        application = TCApplication.objects.create(
            name=name,
            roll_number=roll_number,
            department=department,
            prn=prn,
            reason=reason,
            status='pending'
        )

        # Fetch relevant users
        department_roles = CustomUser.objects.filter(
            role__in=['hod', 'tutor', 'staff'], department=department
        )
        general_roles = CustomUser.objects.filter(
            role__in=['admin', 'nss', 'ncc', 'lab', 'hostel', 'library', 'academics']
        )
        relevant_users = department_roles | general_roles

        # Check and process due status
        is_due = check_and_process_due_status(prn, application, relevant_users)

        if not is_due:
            # If no dues, add reviewers to the pending approval list
            application.pending_approval.add(*relevant_users)
            application.save()

        return redirect('application_status')  # Redirect to the application status page

    return render(request, 'student/user_dashboard.html')



@login_required
def application_status(request):
    """
    View to show the status of a student's TC application.
    """
    if request.user.role != 'student':
        return HttpResponseForbidden("You are not authorized to access the application status page.")

    # Fetch the student's TC application
    application = get_object_or_404(TCApplication, prn=request.user.prn)

    return render(request, 'student/application_status.html', {'application': application})


@login_required
def tc_status(request):
    """
    View to display the detailed status of a student's TC application.
    Includes role-wise status (approved, pending, due).
    """
    if request.user.role != 'student':
        return HttpResponseForbidden("You are not authorized to access the student status page.")

    # Fetch the student's TC application
    application = TCApplication.objects.filter(prn=request.user.prn).first()

    # Get all relevant reviewers (departmental + general)
    department_reviewers = CustomUser.objects.filter(
        role__in=['hod', 'tutor', 'staff'], department=request.user.department
    )
    general_reviewers = CustomUser.objects.filter(
        role__in=['admin', 'nss', 'ncc', 'lab', 'hostel', 'library', 'academics']
    )
    all_reviewers = department_reviewers | general_reviewers

    # Initialize role statuses
    role_statuses = []
    application_status = "pending"

    if application:
        # Iterate through all reviewers to determine their statuses
        for reviewer in all_reviewers:
            if reviewer in application.approved_by.all():
                status = "approved"
            elif reviewer in application.due_list.all():  # Check if marked as due
                status = "due"
                application_status = "due"
            else:
                status = "pending"

            role_statuses.append({
                "name": reviewer.get_full_name() or reviewer.username,
                "role": reviewer.role.capitalize(),
                "status": status,
            })

        # Update the application's overall status
        if application_status != "due" and len(application.approved_by.all()) == all_reviewers.count():
            application_status = "approved"
            application.status = application_status
            application.save()

    context = {
        "application": application,
        "roles": role_statuses,
        "application_status": application_status,
    }

    return render(request, "student/status.html", context)


@login_required
def success_message(request):
    return render(request, 'student/success_message.html')

@login_required
def download_tc_pdf(request, application_id):
    # Fetch the TC application
    try:
        application = TCApplication.objects.get(id=application_id, prn=request.user.username, status='approved')
    except TCApplication.DoesNotExist:
        return HttpResponseForbidden("No approved TC available for download.")

    # Generate PDF
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(100, 750, "Transfer Certificate")
    pdf.drawString(100, 720, f"Name: {application.name}")
    pdf.drawString(100, 700, f"Roll Number: {application.roll_number}")
    pdf.drawString(100, 680, f"Department: {application.department}")
    pdf.drawString(100, 660, f"PRN: {application.prn}")
    pdf.drawString(100, 640, f"Reason: {application.reason}")
    pdf.drawString(100, 620, "Status: Approved")
    pdf.showPage()
    pdf.save()

    # Return the PDF file as a response
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="TC.pdf")


@login_required
def settings(request):
    return render(request, 'student/settings.html')
