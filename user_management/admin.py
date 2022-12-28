from django.contrib import admin
from user_management.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserModelAdmin(BaseUserAdmin):
  list_display = ('id', 'company_name','email', 'is_active')
  list_filter = ('is_active',)
  fieldsets = (
      ('User Credentials', {'fields': ('email', 'password')}),
      ('Personal info', {'fields': ('url','db','key','location_name','company_name')}),
      ('Permissions', {'fields': ('is_admin','is_active')}),
  )
  add_fieldsets = (
      (None, {
          'classes': ('wide',),
          'fields': ('db', 'url', 'key'),
      }),
  )
  search_fields = ('email',)
  ordering = ('email', 'id')
  filter_horizontal = ()


# Now register the new UserModelAdmin...
admin.site.register(User, UserModelAdmin)