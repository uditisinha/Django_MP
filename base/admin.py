from django.contrib import admin
from .models import User,Subjects,Branch,Folder,File


admin.site.register(Subjects)
admin.site.register(Branch)
admin.site.register(User)
admin.site.register(Folder)
admin.site.register(File)

# Register your models here.
