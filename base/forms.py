from django.forms import ModelForm, widgets
from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Folder, File, Subjects, Year, Branch

class FolderForm(ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'parent_directory']

class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['email','password']

class SubjectForm(ModelForm):
    year = forms.ModelMultipleChoiceField(
        queryset=Year.objects.all().order_by('year'),
        widget=forms.CheckboxSelectMultiple(),
        label='Year'
    )
    branch = forms.ModelMultipleChoiceField(
        queryset=Branch.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple(),
        label='Branch'
    )
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all().order_by('email'),
        widget=forms.CheckboxSelectMultiple(),
        label='Viewers'
    )
    editors = forms.ModelMultipleChoiceField(
        queryset=User.objects.all().order_by('email'),
        widget=forms.CheckboxSelectMultiple(),
        label='Editor'
    )

    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)
        self.fields['year'].label_from_instance = lambda obj: obj.year
        self.fields['branch'].label_from_instance = lambda obj: obj.name
        self.fields['members'].label_from_instance = lambda obj: obj.pname+ " -- " + obj.email
        self.fields['editors'].label_from_instance = lambda obj: obj.pname+ " -- " + obj.email

    class Meta:
        model = Subjects
        fields = ['name', 'year', 'branch', 'members', 'editors', 'description']



class MyUserCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
            super(MyUserCreationForm, self).__init__(*args, **kwargs)
            self.fields['pname'].widget.attrs['placeholder'] = 'John Doe'
            self.fields['email'].widget.attrs['placeholder'] = 'example@gmail.com'
            self.fields['username'].widget.attrs['placeholder'] = 'Enter your username'
            self.fields['password1'].widget.attrs['placeholder'] = 'Enter your password'
            self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'

    class Meta:
        model = User
        fields = ['pname', 'email', 'branch', 'year', 'username', 'password1', 'password2']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'pname', 'year']

class ReadOnlyWidget(widgets.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return value

class FileForm(ModelForm):
    class Meta:
        model = File
        fields = '__all__'
        widgets = {
            'subject': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        subject_id = kwargs.pop('subject_id', None)
        super().__init__(*args, **kwargs)
        if subject_id:
            self.fields['subject'].initial = subject_id
