from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from account.views import login_view, logout_view

urlpatterns = [
    path('', login_view, name='default-login'),  # Default root URL points to login_view
    path('admin/', admin.site.urls),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('adminuser/', include('adminuser.urls')),  # Include adminuser app URLs
    path('student/', include('student.urls')),  # Include student app URLs
    path('account/', include('account.urls')),
    path('collegeusers/', include('collegeusers.urls')),
    path('clerks/', include('clerks.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
