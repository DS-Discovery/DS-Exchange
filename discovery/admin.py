from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.admin import AdminSite

class DiscoveryAdmin(AdminSite):
    pass

admin_site = DiscoveryAdmin(name='discovery_admin')
