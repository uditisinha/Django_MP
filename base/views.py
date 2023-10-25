from django.shortcuts import render,redirect
from urllib.parse import unquote
from django.urls import reverse
import time
# from mimetypes import guess_type
from django.http import HttpResponse,FileResponse
from .models import User, Subjects, Folder, File
from .forms import MyUserCreationForm, LoginForm, UserForm, SubjectForm
from django.db.models import Q
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import FolderForm,FileForm
from django.core.mail import EmailMessage
import uuid
from django.core.mail import send_mail
import os


# Create your views here.
@login_required(login_url = 'login')
def home(request):
    if request.user.is_authenticated :
        user = request.user
        subject_list = list(
            Subjects.objects.exclude(
                ~Q(editors = user) & ~Q(members = user)
            )
        )
        context = {
            'subject_list': subject_list,
        }
        return render(request, "base/home.html", context)
    else:
        # Handle the case when the user is not authenticated
        return redirect('login')


@login_required(login_url = 'login')
def subjects_list(request): 

    year = request.user.year
    if request.GET.get('q') != None:
        q = request.GET.get('q', '')
    else:
        q = ''

    selected_subjects = Subjects.objects.filter(
        Q(name__icontains = q),
        year = year
    )

    subjects = Subjects.objects.all()
    context = {'subjects': subjects, 'selected_subjects': selected_subjects}
    return render(request, 'base/subjects_list.html', context)

def loginuser(request):
    page = 'login'
    form = LoginForm()

    if(request.user.is_authenticated):
        return redirect('home')
    
    if (request.method == "POST"):

            email = request.POST.get('email')
            password = request.POST.get('password')

            user_email = request.POST.get('email')

            #checks whether user exists
            try:
                email = User.objects.get(email = email)
            except:
                messages.error(request, 'User does not exist.')

            #checks for the user with given mail and password
            user = authenticate(request, email = user_email, password = password)
            
            if user != None:
                if user.is_verified:
                    if user.is_superuser:
                        login(request,user)
                        messages.success(request,'Login Successful, Welcome Admin!')
                        return redirect('home')
                    login(request,user)
                    messages.success(request, 'Login Successful!')
                    return redirect('home')
                else:
                    messages.error(request, 'Please verify your email.')
            else:
                messages.error(request,'Incorrect Password.')

    context={
        'page':page,
        'form':form
    }

    return render(request,'base/login_register.html',context)


def forgot_password(request):

    if request.user.is_authenticated:
        return redirect('home')
    
    try:
        if request.method == "POST":

            email = request.POST.get('email')

            if User.objects.filter(email = email).first():
                email_obj = email
                print(email_obj)
                token = str(uuid.uuid4())
                user_obj = User.objects.get(email = email_obj)
                user_obj.password_token = token
                user_obj.save()
                send_forget_password_mail(email_obj, token)
                messages.success(request, 'An email is sent!')
                return redirect ('/')

            else:
                messages.error(request, 'User does not exist.')
        
    except Exception as e:
        print(e)

    return render (request, 'base/forgot_password.html')


def send_forget_password_mail(email, token):
    subject = "Your forgot password link"
    message = f"http://127.0.0.1:8000/change_password/{token}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True

def send_change_password_mail(email, token):
    subject = "Your change password link"
    message = f"http://127.0.0.1:8000/change_password/{token}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True

def change_password(request, token):
    context = {}

    try:
        if request.method == "POST":
            user_obj = User.objects.filter(password_token = token).first()
            context = {'user_id': user_obj.id}
            new_password = request.POST.get('password1')
            confirm_password = request.POST.get('password2')
            user_id = context['user_id']

            if new_password != confirm_password:
                messages.error(request, 'The passwords do not match.')
                return redirect(f'/change_password/{token}')
            
            user_obj = User.objects.get(id=user_id)
            user_obj.set_password(new_password)
            user_obj.save()
            messages.success(request, 'Password changed successfully! Please login with your new password.')
            return redirect('/')

    except Exception as e:
        print(e)
        messages.error(request, 'Expired link.')
        return render (request, 'base/error.html')

    if request.user.is_authenticated:
        return render(request, 'base/change_password_loggedin.html', context)
    
    else:
        return render(request, 'base/change_password.html', context)


@login_required(login_url = 'login')
def logoutuser(request):
    logout(request)
    messages.success(request, 'Successfully Logged Out.')
    return redirect('home')


def registeruser(request):
    form = MyUserCreationForm()
    page = 'register'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']

            # Check if a user with the provided email already exists
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                if not existing_user.is_verified:
                    messages.error(request, 'Email has been sent to you for verification.')

            else:
                if email != None:

                    user.username = username.lower()
                    user.auth_token = str(uuid.uuid4())
                    token = user.auth_token
                    user.save()

                    send_mail_for_registration(email, token)
                    messages.error(request, 'Please click on the link mailed to your email ID to verify account.')

                    return redirect('/')
                
                else:
                    messages.error(request, 'You are not authorized. Please contact the HOD for authorization.')

    context = {'form': form, 'page': page}
    return render(request, 'base/login_register.html', context)


def success(request):
    return render(request, 'base/success.html')

def sending_token(request):
    return render(request, 'base/sending_token.html')

def send_mail_for_registration(email, token):
    subject = "Your verification mail for CourseDocs"
    message = f"Please click on this link to verify your email and Log in - http://127.0.0.1:8000/verify/{token}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)

def verify(request, auth_token):
    try:
        user_obj = User.objects.filter(auth_token=auth_token).first()

        if user_obj:
            if user_obj.is_verified:
                messages.success(request, 'Your email is already verified.')
                return redirect('/')
            else:
                user_obj.is_verified = True
                user_obj.save()
                messages.success(request, 'Your account has been verified!')
                login(request, user_obj)
                return redirect('home')

        return redirect('error')

    except Exception as e:
        print(e)

def error(request):
    return render(request, 'base/error.html')

@login_required(login_url = 'login')
def edit_profile(request, pk):
    user = User.objects.get(id = pk)
    if request.user!=user:
        return redirect('home')
    form = UserForm(instance=user)
    if request.method == 'POST' and 'submit' in request.POST.keys():
        form = UserForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile', pk)
    if request.method=='POST' and 'Change Password' in request.POST.keys():
        user_obj = request.user
        token = str(uuid.uuid4())
        user_obj.password_token = token
        user_obj.save()
        email_obj = request.user.email
        send_change_password_mail(email_obj, token)
        messages.success(request, 'Click on the link mailed to you to change the password.')
        return redirect ('/')
    context={
        'form':form
    }
    return render(request,'base/edit_profile.html',context)

@login_required(login_url = 'login')
def profile(request,pk):
    user = User.objects.get(id=pk)
    Subjects =  list(
        Subjects.objects.exclude(
                ~Q(editors = user) & ~Q(members = user)
            ))
    
    context={
        'Subjects':Subjects,
        'user':user
    }
    return render(request,'base/profile.html',context)

@login_required(login_url = 'login')
def subs(request, pk):
    subject = Subjects.objects.get(id = pk)
    path = str(settings.MEDIA_ROOT) + '/files/' + subject.name + '/'
    files = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            item_url = str(settings.MEDIA_URL) + 'files/' + subject.name + '/' + item + '/'
            files.append([item,item_url])
    context = {'subject': subject,'folders':files}
    return render(request, 'base/subs.html', context)


@login_required(login_url = 'login')
def delete_subject(request, pk):
    subject = Subjects.objects.get(id = pk)

    if not request.user.is_superuser:
        return HttpResponse('Only the admin can delete the subject.')
    
    if request.method == "POST":
        subject.delete()
        return redirect('subject_list')
    
    context = {'obj': subject}
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def create_subject(request):
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            folder_name = subject.name
            path = str(settings.MEDIA_ROOT) + '\\files/' + f'{folder_name}/'
            os.makedirs(path)
            print('idhar issue hua')
            new_folder = Folder()
            new_folder.name = folder_name
            new_folder.parent_directory = path
            new_folder.save() 
            subject.save()
            form.save_m2m()  # Save the many-to-many relationships
            messages.success(request, "Subject added successfully!")
            return redirect('subjects_list')
    else:
        form = SubjectForm()
    
    context = {'form': form}
    return render(request, 'base/add_subject.html', context)

@login_required(login_url = 'login')
def filesview(request,path='',filename=''):
    file_path = os.path.join(settings.MEDIA_ROOT, 'files', path, filename)
    try:
        with open(file_path, 'rb') as file:
            response = FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    except FileNotFoundError:
        return HttpResponse('File not found', status=404)


@login_required(login_url = 'login')
def deletefile(request,pk):
    del_file = File.objects.get(id=pk)
    if request.method =='POST':
        del_file.delete()
        return redirect(settings.MEDIA_URL + 'files/')
    context={
        'obj':del_file
    }
    return render(request,'base/delete.html',context)

@login_required(login_url = 'login')
def search_files(request):
    if request.GET.get('q') != None:
        q = request.GET.get('q')
    else:
        q = ''
    user = request.user
    Subjects = Subjects.objects.filter(members=user) | Subjects.objects.filter(editors=user)
    filtered_files = File.objects.filter(
        (Q(name__icontains = q) | Q(keywords__icontains = q) | Q(subject__name__icontains = q))
    )
    subject_list=[]
    for c in Subjects:
        subject_list.append(c.name)
    bool_list=[]
    search_file_paths=[]
    for file in filtered_files:
        search_file_paths.append(str(settings.MEDIA_URL) + str(file.file))
        if str(file.subject) in subject_list:
            bool_list.append(True)
        else:
            bool_list.append(False)

    files_context = []
    for i in range(len(filtered_files)):
        files_context.append([filtered_files[i],search_file_paths[i],bool_list[i]])
    context={
        'Subjects':subject_list,
        'files_context':files_context,
        'search_files':filtered_files,
        'search_file_paths':search_file_paths,
    }
    return render(request,'base/searched-files.html',context)
    
@login_required(login_url = 'login')
def filestructure(request,path=''):
    if request.GET.get('q') != None:
        q = request.GET.get('q')
    else:
        q = ''
    subject_id = None
    flag=0
    flag2=0
    user = request.user
    subject_names=[]
    user_Subjects = Subjects.objects.filter(members=user) | Subjects.objects.filter(editors=user)
    if user.is_superuser:
        user_Subjects = Subjects.objects.all()
    for names in user_Subjects:
        subject_names.append(names.name)
    current_url = request.build_absolute_uri()
    base_url = request.build_absolute_uri('/')
    media_url = settings.MEDIA_URL[1:] # Get the base URL with protocol and domain
    files_url = base_url + media_url + 'files/' # Combine base URL with MEDIA_URL
    for subject in subject_names:
       url = files_url+subject
       if (url in unquote(current_url)):
           subject_id = Subjects.objects.get(name=subject)
           flag=1 
    if (flag==0 and current_url!=files_url):
        flag2=1
        print(flag2)
    if(current_url!=files_url):
        parts = current_url.split('/')
        back_url = '/'.join(parts[:-2]) + '/'
    else:
        print('invalid')
        back_url = None
    updated_access_parameters = current_url.rsplit("media/",1)[1]
    updated_access_parameters = updated_access_parameters.rsplit("?q",1)[0]
    print(updated_access_parameters)
    checker_for_main_file = current_url.rsplit("media/files/",1)[1]
    updated_access_parameters = unquote(updated_access_parameters)
    if(len(checker_for_main_file)>0):
        this_is_first_folder = '0'
    else:
        this_is_first_folder = '1'
    path_to = os.path.join(str(settings.MEDIA_ROOT),updated_access_parameters)
    path_to_2 = None
    if(path_to[-1]!='/'):
        path_to_2 = path_to+'/'
    if(path_to_2!=None):
        files_to_access = File.objects.filter(Q(directory=path_to)|Q(directory=path_to_2))
    else:
        path_to_3 = path_to[:-1]
        files_to_access = File.objects.filter(Q(directory=path_to)|Q(directory=path_to_3))
    if q!='':
        current_url = current_url.rsplit("?q",1)[0]
        files_to_access = File.objects.filter(
        Q(name__icontains = q) | Q(keywords__icontains = q) | Q(subject__name__icontains = q),id__in = files_to_access)
    file_paths = []
    file_extensions = []
    i=0
    for file in files_to_access:
        file_paths.append(str(settings.MEDIA_URL) + str(file.file))
        file_extension = file_paths[i].split('.')[-1]  # Extract the extension and convert to lowercase
        file_extensions.append(file_extension)
        i+=1
    files = []
    for item in os.listdir(path_to):
        item_path = os.path.join(path_to, item)
        if os.path.isdir(item_path):
            files.append(item)
        # else:
        #     files.append(f'File: {item}')
    form = FolderForm()
    if subject_id is not None:
        form2 = FileForm(subject_id = subject_id)
    else:
        form2=FileForm()
    if request.method == "POST" and 'first_post' in request.POST.keys():
        form = FolderForm(request.POST)
        if not form.is_valid():
            # Create a mutable copy of request.POST
            post_data = request.POST.copy()
            
            # Clean and modify the form data in the copied dictionary
            post_data['parent_directory'] = os.path.join(post_data['parent_directory'], post_data['name'] + '/')
            
            # Reconstruct the form with the modified data
            form = FolderForm(post_data)
            
            # Re-validate the modified form
            if form.is_valid():
                directory = form.save(commit=False)
                os.makedirs(directory.parent_directory)
                directory.save()
                
                return redirect(current_url)
            else:
                print(form.errors)
                print("ERROR")
        else:
            if form.is_valid():
                directory = form.save(commit=False)
                directory_name = directory.name + '/'
                directory.parent_directory = os.path.join(directory.parent_directory, directory_name)
                os.makedirs(directory.parent_directory)
                directory.save()
                return redirect(current_url)
            else:
                print("ERROR")

    if request.method == "POST" and 'second_post' in request.POST.keys():
        form2 = FileForm(request.POST,request.FILES)
        if(form2.is_valid()):
            form2.save()
            return redirect(current_url)
        else:
            print("NOT VALID")
    
    files_context=[]

    for i in range(len(file_paths)):
        files_context.append([files_to_access[i],file_paths[i],file_extensions[i]])

    context = {
        'files_context':files_context, 
        'directory':path_to,
        'form':form,
        'check2':flag2,
        'files':files,
        'form2':form2,
        'check':this_is_first_folder,
        'files_to_access':files_to_access,
        'file_paths':file_paths,
        'current_url':current_url,
        'back_url':back_url,
        'subject_names':subject_names,
    }
    return render(request,'base/file_structure.html',context)