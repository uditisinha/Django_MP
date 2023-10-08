from django.contrib import admin
from .models import User,Subjects,Branch,Folder,File, Year


admin.site.register(Subjects)
admin.site.register(Year)
admin.site.register(Branch)
admin.site.register(User)
admin.site.register(Folder)
admin.site.register(File)

# Register your models here.
