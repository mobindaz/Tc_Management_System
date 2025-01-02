from django.contrib import admin
from .models import TCApplication

class TCApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'department', 'status', 'updated_at')  # Ensure updated_at is defined
    list_filter = ('status', 'department', 'updated_at')  # Ensure updated_at is defined
    search_fields = ('name', 'roll_number', 'prn')

admin.site.register(TCApplication, TCApplicationAdmin)
