from django.contrib import admin

from . import models
from .models import User


#Following registers objects that are managed by admin
admin.site.unregister(User)
#admin.site.register(User, MyUserAdmin)
admin.site.register(models.Item)
admin.site.register(models.UserProfile)
admin.site.register(models.ConfirmString)
