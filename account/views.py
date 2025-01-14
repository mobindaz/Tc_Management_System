from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

CustomUser = get_user_model()


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        # Check if the user exists
        if not CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username not found.Contact admin.")
            return redirect('login')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)

            # Redirect based on role
            if user.is_superuser or getattr(user, 'role', None) == 'admin':
                return redirect('admin_panel')  # Replace with your admin dashboard URL
            elif getattr(user, 'role', None) == 'hod':
                return redirect('hod_dashboard')
            elif getattr(user, 'role', None) == 'tutor':
                return redirect('tutor_dashboard')
            elif getattr(user, 'role', None) == 'staff':
                return redirect('staff_dashboard')
            elif getattr(user, 'role', None) == 'nss':
                return redirect('nss_dashboard')
            elif getattr(user, 'role', None) == 'ncc':
                return redirect('ncc_dashboard')
            elif getattr(user, 'role', None) == 'lab':
                return redirect('lab_dashboard')
            elif getattr(user, 'role', None) == 'hostel':
                return redirect('hostel_dashboard')
            elif getattr(user, 'role', None) == 'library':
                return redirect('library_dashboard')
            elif getattr(user, 'role', None) == 'academics':
                return redirect('academics_dashboard')
            elif getattr(user, 'role', None) == 'clerks':
                return redirect('clerk_dashboard')
            elif getattr(user, 'role', None) == 'student':
                return redirect('user_dashboard')  # Replace with your student dashboard URL
            else:
                messages.error(request, "Unauthorized role. Contact the admin.")
                return redirect('login')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
