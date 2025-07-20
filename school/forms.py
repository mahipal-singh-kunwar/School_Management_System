from django import forms
from django.contrib.auth.models import User
from . import models

#for admin
class AdminSigupForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']


#for student related form
class StudentUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
class StudentExtraForm(forms.ModelForm):
    class Meta:
        model=models.StudentExtra
        fields=['roll','cl','mobile','fee','status']


#for teacher releted form
# Teacher UserForm
class TeacherUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']

class TeacherExtraForm(forms.ModelForm):
    department = forms.ChoiceField(
        choices=[('', 'Select Department')] + models.DEPARTMENTS,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )

    class Meta:
        model = models.TeacherExtra
        fields = ['salary', 'mobile', 'department', 'status']
        widgets = {
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Salary (₹)'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact'}),
        }




#for Attendance related form
presence_choices = (('Present', 'Present'), ('Absent', 'Absent'))

presence_choices=(('Present','Present'),('Absent','Absent'))
class AttendanceForm(forms.Form):
    present_status=forms.ChoiceField( choices=presence_choices)
    date=forms.DateField()

class AskDateForm(forms.Form):
    date=forms.DateField()




#for notice related form
class NoticeForm(forms.ModelForm):
    class Meta:
        model=models.Notice
        fields='__all__'



#for contact us page
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))
