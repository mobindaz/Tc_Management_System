from django.core.management.base import BaseCommand
from collegeusers.models import AutoApprovalSettings
from student.models import TCApplication, UploadedDueList


class Command(BaseCommand):
    help = 'Process all pending TC applications for auto-approval'

    def handle(self, *args, **kwargs):
        # Get all users with auto-approval enabled
        auto_approval_users = AutoApprovalSettings.objects.filter(auto_approval_enabled=True)

        if not auto_approval_users.exists():
            self.stdout.write(self.style.WARNING("No users have auto-approval enabled."))
            return

        for setting in auto_approval_users:
            user = setting.user
            self.stdout.write(f"Processing auto-approval for user: {user.username}")

            # Get all applications pending for this user (no time-based filtering)
            pending_apps = TCApplication.objects.filter(
                pending_approval=user,
                status='pending'
            )

            self.stdout.write(f"Found {pending_apps.count()} pending applications for user: {user.username}")

            for app in pending_apps:
                self.stdout.write(f"Processing Application ID: {app.id}, PRN: {app.prn}")

                # Check if the PRN exists in the uploaded due list for this user
                matching_due = UploadedDueList.objects.filter(prn=app.prn, added_by=user)

                if matching_due.exists():
                    # Move to due list for this user
                    app.due_users.add(user)
                    self.stdout.write(f"Application ID: {app.id} moved to 'due' for user: {user.username}")
                else:
                    # Approve the application for this user only
                    app.approved_by.add(user)
                    app.pending_approval.remove(user)  # Remove this user from the pending list
                    self.stdout.write(f"Application ID: {app.id} approved for user: {user.username}")

                # Save changes to the application
                app.save()

        self.stdout.write(self.style.SUCCESS('Successfully processed auto-approval.'))
