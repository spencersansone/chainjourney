from django.contrib import admin
from .models import *

#Allows for the admin to edit database objects in models from
#django administration

admin.site.register(PayoutPeriod)
admin.site.register(Period)
admin.site.register(UserProfile)
admin.site.register(Phase)

