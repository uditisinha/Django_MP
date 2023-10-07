from django.forms import ModelForm, widgets
from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Folder, File, Committees, UserList

class FolderForm(ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'parent_directory']

class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['email','password']

class SubjectForm(ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all().order_by('email'),
        widget=forms.CheckboxSelectMultiple(),
        label='Members'
    )
    editors = forms.ModelMultipleChoiceField(
        queryset=User.objects.all().order_by('email'),
        widget=forms.CheckboxSelectMultiple(),
        label='Editors'
    )

    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)
        self.fields['members'].label_from_instance = lambda obj: obj.pname + " -- "  + obj.email
        self.fields['staff'].label_from_instance = lambda obj: obj.pname+ " -- " + obj.email
        self.fields['convener'].label_from_instance = lambda obj: obj.pname+ " -- " + obj.email

    class Meta:
        model = Committees
        fields = '__all__'


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['honorific', 'pname', 'email', 'number', 'department', 'position', 'username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
            super(MyUserCreationForm, self).__init__(*args, **kwargs)
            self.fields['honorific'].widget.attrs['placeholder'] = 'Ms./Mr.'
            self.fields['pname'].widget.attrs['placeholder'] = 'John Doe'
            self.fields['email'].widget.attrs['placeholder'] = 'example@gmail.com'
            self.fields['number'].widget.attrs['placeholder'] = 'Enter your phone number'
            self.fields['department'].widget.attrs['values'] = 'Select your department'
            self.fields['position'].widget.attrs['placeholder'] = 'Assistant Professor'
            self.fields['username'].widget.attrs['placeholder'] = 'Enter your username'
            self.fields['password1'].widget.attrs['placeholder'] = 'Enter your password'
            self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'honorific', 'pname', 'number', 'department', 'position']

class UserListForm(ModelForm):
    class Meta:
        model = UserList
        fields = ['email']

class ReadOnlyWidget(widgets.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return value

class FileForm(ModelForm):
    class Meta:
        model = File
        fields = '__all__'
        widgets = {
            'committee': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        committee_id = kwargs.pop('committee_id', None)
        super().__init__(*args, **kwargs)
        if committee_id:
            self.fields['committee'].initial = committee_id
