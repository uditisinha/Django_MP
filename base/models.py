from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import os
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import shutil
    

from django.contrib.auth.models import AbstractUser
from django.db import models

class Year(models.Model):
    year = models.CharField(max_length=200, null=False)
    subjects = models.ManyToManyField('Subjects', related_name='years', null=True, blank=True)

    def __str__(self):
        return self.year
    
class User(AbstractUser):
    avatar = models.ImageField(null=True, upload_to="images/", blank=True)
    pname = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    year = models.ForeignKey(Year, on_delete=models.CASCADE, null=True)
    branch = models.ForeignKey('Branch', on_delete=models.SET_NULL, null=True)
    is_verified = models.BooleanField(default=False, null=True)
    auth_token = models.CharField(max_length=200, null=True)
    password_token = models.CharField(max_length=200, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['pname', 'username']

    def __str__(self):
        return self.username

class Subjects(models.Model):
    name = models.CharField(max_length=200)
    year = models.ManyToManyField(Year, related_name='subject_year')
    branch = models.ManyToManyField('Branch', related_name='subject_branch')
    description = models.TextField(max_length=1000, null=True)
    editors = models.ManyToManyField(User, related_name='subject_editors', null=True, blank=True)

    def __str__(self):
        return self.name

class Branch(models.Model):
    name = models.CharField(max_length=200)
    subjects = models.ManyToManyField(Subjects, related_name='subjects', null=True, blank=True)

    def __str__(self):
        return self.name
    

class Folder(models.Model):
    name = models.CharField(max_length=10000)
    parent_directory = models.CharField(unique=True,max_length=10000,default=os.path.join(settings.MEDIA_ROOT, "files/"))
    def __str__(self):
        return self.name
    

@receiver(pre_delete,sender=Subjects)
def delete_subject_folder(sender,instance,**kwargs):
    folder_name = instance.name
    path = str(settings.MEDIA_ROOT) +'\\files/'+f'{folder_name}/'


@receiver(pre_delete, sender=Folder)
def delete_subfolders(sender, instance, **kwargs):
    # Temporarily disconnect the signal to avoid recursion
    pre_delete.disconnect(delete_subfolders, sender=Folder)
    try:
        # Delete subfolders in bulk
        subfiles = File.objects.filter(directory__startswith=instance.parent_directory)
        subfolders = Folder.objects.filter(parent_directory__startswith=instance.parent_directory)
        subfolders.delete()
        subfiles.delete()
        try:
            shutil.rmtree(instance.parent_directory)
        except OSError as e:
            print(f"Error deleting directory: {e}")
    finally:
        # Reconnect the signal after the deletion is done
        pre_delete.connect(delete_subfolders, sender=Folder)

def generate_upload_path(instance,name):
    directory = instance.directory
    return f'{directory}\{name}'

class File(models.Model):
    def __str__(self):
        return os.path.basename(self.file.name)
    
    name = models.CharField(max_length=500,null=False)
    file = models.FileField(max_length=20000,upload_to=generate_upload_path)
    keywords = models.TextField(max_length=1000,null=True,blank=True)
    directory = models.CharField(max_length=10000)
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE,null=True,blank=True)

@receiver(pre_delete,sender=File)
def delete_files(sender,instance,**kwargs):
    try:
        # Delete the file from the file system
        path =instance.file.path
        os.remove(path)
        print(f"File '{path}' deleted successfully.")
    except OSError as e:
        print(f"Error deleting file: {e}")