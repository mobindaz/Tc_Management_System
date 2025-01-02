from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from student.models import TCApplication
from django.http import HttpResponseForbidden, FileResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from adminuser.models import CustomUser

@login_required
def user_dashboard(request):
    if request.user.role != 'student':
        return HttpResponseForbidden("You are not authorized to access the student dashboard.")
    
    # Fetch the student's TC application
    application = TCApplication.objects.filter(prn=request.user.username).first()

    # Handle TC application submission
    if request.method == 'POST':
        # Check if the student already has an active application
        if application:
            return redirect('user_dashboard')  # Redirect to dashboard if application exists

        # Fetch data from the POST request
        name = request.POST.get('name')
        roll_number = request.POST.get('roll_number')
        department = request.POST.get('department')
        prn = request.user.username  # Use the logged-in user's PRN
        reason = request.POST.get('reason')

        # Create a TC application
        application = TCApplication.objects.create(
            name=name,
            roll_number=roll_number,
            department=department,
            prn=prn,
            reason=reason,
            status='pending'
        )

        # Attach all non-student users to the application
        reviewers = CustomUser.objects.exclude(role='student')
        application.pending_approval.add(*reviewers)
        application.save()

        return redirect('success_message')  # Redirect to the success page

    context = {
        'application': application
    }
    return render(request, 'student/user_dashboard.html', context)


@login_required
def tc_status(request):
    # Check if the logged-in user is a student
    if request.user.role != 'student':
        return HttpResponseForbidden("You are not authorized to access the student status page.")

    # Fetch the student's TC application
    application = TCApplication.objects.filter(prn=request.user.username).first()

    # Get all roles except "student"
    roles = CustomUser.objects.exclude(role='student')

    # Initialize variables
    role_statuses = []
    application_status = "pending"  # Default application status

    if application:
        # Iterate through roles to determine status for each
        for role in roles:
            if role in application.approved_by.all():
                status = "approved"
            elif role in application.due_list.all():  # Check if the role marked it as due
                status = "due"
                application_status = "due"  # Update the application status if any role marks as due
            else:
                status = "pending"

            role_statuses.append({
                "name": role.role.capitalize(),
                "user": role.username,
                "status": status,
            })

        # If no "due" and all roles have approved, mark as approved
        if application_status != "due" and len(application.approved_by.all()) == roles.count():
            application_status = "approved"

        # Update application status and save
        application.status = application_status
        application.save()
    else:
        # Handle case where the student has no application
        for role in roles:
            role_statuses.append({
                "name": role.role.capitalize(),
                "user": role.username,
                "status": "pending",
            })

    # Count approved roles for display
    approved_count = len([role for role in role_statuses if role["status"] == "approved"])

    context = {
        "application": application,
        "roles": role_statuses,
        "approved_count": approved_count,
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
