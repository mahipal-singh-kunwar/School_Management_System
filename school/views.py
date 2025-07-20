from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum, Count
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from .models import Profile
import razorpay
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import StudentExtra, Attendance
from django.db.models.functions import TruncMonth



import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Event  

# calender view for adminnnnnnnnnnnnnnnnnnnnnnnn




def profile_detail(request, slug):
    profile = get_object_or_404(Profile, slug=slug)
    return render(request, 'school/profile_detail.html', {'profile': profile})


def home_view(request):
    if request.user.is_authenticated:
        return redirect('afterlogin')
    return render(request,'school/index.html')

def contact(request):
    return render(request, 'school/contact.html')


#for showing signup/login button for teacher
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'school/adminclick.html')


#for showing signup/login button for teacher
def teacherclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'school/teacherclick.html')


#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'school/studentclick.html')





def admin_signup_view(request):
    form=forms.AdminSigupForm()
    if request.method=='POST':
        form=forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.set_password(user.password)
            user.save()


            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)

            return redirect('adminlogin')  #

    return render(request,'school/adminsignup.html',{'form':form})



def student_signup_view(request):
    form1=forms.StudentUserForm()
    form2=forms.StudentExtraForm()
    mydict={'form1':form1,'form2':form2}
    if request.method=='POST':
        form1=forms.StudentUserForm(request.POST)
        form2=forms.StudentExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()
            f2=form2.save(commit=False)
            f2.user=user
            user2=f2.save()

            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        return redirect('studentlogin')
                   
        return redirect('studentlogin')
    #    return HttpResponseRedirect('studentlogin')
    return render(request,'school/studentsignup.html',context=mydict)


def teacher_signup_view(request):
    form1=forms.TeacherUserForm()
    form2=forms.TeacherExtraForm()
    mydict={'form1':form1,'form2':form2}
    if request.method=='POST':
        form1=forms.TeacherUserForm(request.POST)
        form2=forms.TeacherExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()
            f2=form2.save(commit=False)
            f2.user=user
            user2=f2.save()

            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)
                        #  Only redirect if form is valid
            return redirect('teacherlogin')
    return render(request,'school/teachersignup.html',context=mydict)



#for checking user is techer , student or admin
def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()
def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()
def is_student(user):
    return user.groups.filter(name='STUDENT').exists()


def afterlogin_view(request):
    if is_admin(request.user):
        return redirect('admin-dashboard')
    elif is_teacher(request.user):
        accountapproval=models.TeacherExtra.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('teacher-dashboard')
        else:
            return render(request,'school/teacher_wait_for_approval.html')
    elif is_student(request.user):
        accountapproval=models.StudentExtra.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('student-dashboard')
        else:
            return render(request,'school/student_wait_for_approval.html')




#for dashboard of adminnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    teachercount = models.TeacherExtra.objects.filter(status=True).count()
    pendingteachercount = models.TeacherExtra.objects.filter(status=False).count()

    studentcount = models.StudentExtra.objects.filter(status=True).count()
    pendingstudentcount = models.StudentExtra.objects.filter(status=False).count()

    teachersalary = models.TeacherExtra.objects.filter(status=True).aggregate(Sum('salary'))
    pendingteachersalary = models.TeacherExtra.objects.filter(status=False).aggregate(Sum('salary'))

    studentfee = models.StudentExtra.objects.filter(status=True).aggregate(Sum('fee'))
    pendingstudentfee = models.StudentExtra.objects.filter(status=False).aggregate(Sum('fee'))

    notice = models.Notice.objects.all()

    # 📊 Monthly Attendance Chart
    attendance_qs = models.Attendance.objects.annotate(month=TruncMonth('date')).values('month').annotate(count=Count('id'))
    attendance_data = {item['month'].strftime('%b %Y'): item['count'] for item in attendance_qs}

    # 📈 Monthly Fee Chart
    fee_qs = models.StudentExtra.objects.filter(status=True).annotate(month=TruncMonth('admission_date')).values('month').annotate(total=Sum('fee'))
    fee_data = {item['month'].strftime('%b %Y'): item['total'] for item in fee_qs}

    mydict = {
        'teachercount': teachercount,
        'pendingteachercount': pendingteachercount,
        'studentcount': studentcount,
        'pendingstudentcount': pendingstudentcount,
        'teachersalary': teachersalary['salary__sum'],
        'pendingteachersalary': pendingteachersalary['salary__sum'],
        'studentfee': studentfee['fee__sum'],
        'pendingstudentfee': pendingstudentfee['fee__sum'],
        'notice': notice,
        'attendance_json': json.dumps(attendance_data),
        'fee_json': json.dumps(fee_data),
    }

    return render(request, 'school/admin_dashboard.html', context=mydict)




#for teacher sectionnnnnnnn by adminnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_teacher_view(request):
    return render(request,'school/admin_teacher.html')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_teacher_view(request):
    form1=forms.TeacherUserForm()
    form2=forms.TeacherExtraForm()
    mydict={'form1':form1,'form2':form2}
    if request.method=='POST':
        form1=forms.TeacherUserForm(request.POST)
        form2=forms.TeacherExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()

            f2=form2.save(commit=False)
            f2.user=user
            f2.status=True
            f2.save()

            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)
            return redirect('admin-teacher')
        
    return render(request,'school/admin_add_teacher.html',context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_teacher_view(request):
    teachers=models.TeacherExtra.objects.all().filter(status=True)
    return render(request,'school/admin_view_teacher.html',{'teachers':teachers})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_teacher_view(request):
    teachers=models.TeacherExtra.objects.all().filter(status=False)
    return render(request,'school/admin_approve_teacher.html',{'teachers':teachers})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_teacher_view(request,pk):
    teacher=models.TeacherExtra.objects.get(id=pk)
    teacher.status=True
    teacher.save()
    return redirect(reverse('admin-approve-teacher'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_teacher_view(request,pk):
    teacher=models.TeacherExtra.objects.get(id=pk)
    user=models.User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return redirect('admin-approve-teacher')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_teacher_from_school_view(request,pk):
    teacher=models.TeacherExtra.objects.get(id=pk)
    user=models.User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return redirect('admin-view-teacher')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_teacher_view(request,pk):
    teacher=models.TeacherExtra.objects.get(id=pk)
    user=models.User.objects.get(id=teacher.user_id)

    form1=forms.TeacherUserForm(instance=user)
    form2=forms.TeacherExtraForm(instance=teacher)
    mydict={'form1':form1,'form2':form2}

    if request.method=='POST':
        form1=forms.TeacherUserForm(request.POST,instance=user)
        form2=forms.TeacherExtraForm(request.POST,instance=teacher)
        print(form1)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()
            f2=form2.save(commit=False)
            f2.status=True
            f2.save()
            return redirect('admin-view-teacher')
    return render(request,'school/admin_update_teacher.html',context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_teacher_salary_view(request):
    teachers=models.TeacherExtra.objects.all()
    return render(request,'school/admin_view_teacher_salary.html',{'teachers':teachers})






#for student by adminnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_student_view(request):
    return render(request,'school/admin_student.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_student_view(request):
    form1=forms.StudentUserForm()
    form2=forms.StudentExtraForm()
    mydict={'form1':form1,'form2':form2}
    if request.method=='POST':
        form1=forms.StudentUserForm(request.POST)
        form2=forms.StudentExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            print("form is valid")
            user=form1.save()
            user.set_password(user.password)
            user.save()

            f2=form2.save(commit=False)
            f2.user=user
            f2.status=True
            f2.save()

            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        else:
            print("form is invalid")
            return redirect('admin-student')
    return render(request,'school/admin_add_student.html',context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_student_view(request):
    students=models.StudentExtra.objects.all().filter(status=True)
    return render(request,'school/admin_view_student.html',{'students':students})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_student_from_school_view(request,pk):
    student=models.StudentExtra.objects.get(id=pk)
    user=models.User.objects.get(id=student.user_id)
    user.delete()
    student.delete()
    return redirect('admin-view-student')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_student_view(request,pk):
    student=models.StudentExtra.objects.get(id=pk)
    user=models.User.objects.get(id=student.user_id)
    user.delete()
    student.delete()
    return redirect('admin-approve-student')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_student_view(request,pk):
    student=models.StudentExtra.objects.get(id=pk)
    user=models.User.objects.get(id=student.user_id)
    form1=forms.StudentUserForm(instance=user)
    form2=forms.StudentExtraForm(instance=student)
    mydict={'form1':form1,'form2':form2}
    if request.method=='POST':
        form1=forms.StudentUserForm(request.POST,instance=user)
        form2=forms.StudentExtraForm(request.POST,instance=student)
        print(form1)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()
            f2=form2.save(commit=False)
            f2.status=True
            f2.save()
            return redirect('admin-view-student')
    return render(request,'school/admin_update_student.html',context=mydict)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_student_view(request):
    students=models.StudentExtra.objects.all().filter(status=False)
    return render(request,'school/admin_approve_student.html',{'students':students})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_student_view(request,pk):
    students=models.StudentExtra.objects.get(id=pk)
    students.status=True
    students.save()
    return redirect(reverse('admin-approve-student'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_student_fee_view(request):
    students=models.StudentExtra.objects.all()
    return render(request,'school/admin_view_student_fee.html',{'students':students})






#attendance related viewwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_attendance_view(request):
    return render(request,'school/admin_attendance.html')


from django.forms import formset_factory
from .forms import AttendanceForm
import datetime
from .models import StudentExtra, Attendance

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_take_attendance_view(request, cl):
    students = StudentExtra.objects.filter(cl=cl)
    
    if request.method == 'POST':
        date = request.POST.get('date')
        for student in students:
            status = request.POST.get(str(student.id))  # 'Present' or 'Absent'
            if date and status:
                Attendance.objects.create(
                    student=student,
                    date=date,
                    status=status
                )
        return redirect('admin-view-attendance', cl=cl)

    today = datetime.date.today()
    return render(request, 'school/admin_take_attendance.html', {
        'students': students,
        'date': today,
        'cl': cl
    })

from .forms import AskDateForm

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_attendance_view(request, cl):
    form = forms.AskDateForm()

    if request.method == 'POST':
        form = forms.AskDateForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']

            # Get all students in the class
            students = models.StudentExtra.objects.filter(cl=cl)
            attendances = models.Attendance.objects.filter(date=date, student__cl=cl)

            mylist = []

            for student in students:
                status = 'Absent'  # Default
                for att in attendances:
                    if att.student.id == student.id:
                        status = att.status
                        break
                mylist.append({'student': student, 'status': status})

            return render(request, 'school/admin_view_attendance_page.html', {
                'cl': cl,
                'date': date,
                'mylist': mylist
            })

    return render(request, 'school/admin_view_attendance_ask_date.html', {
        'cl': cl,
        'form': form
    })


#fee related view by adminnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_fee_view(request):
    return render(request,'school/admin_fee.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_fee_view(request,cl):
    feedetails=models.StudentExtra.objects.all().filter(cl=cl)
    return render(request,'school/admin_view_fee.html',{'feedetails':feedetails,'cl':cl})








#notice related viewsssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_notice_view(request):
    form=forms.NoticeForm()
    if request.method=='POST':
        form=forms.NoticeForm(request.POST)
        if form.is_valid():
            form=form.save(commit=False)
            form.by=request.user.first_name
            form.save()
            return redirect('admin-dashboard')
    return render(request,'school/admin_notice.html',{'form':form})








#for TEACHER  LOGIN    SECTIONNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN
@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    teacherdata=models.TeacherExtra.objects.all().filter(status=True,user_id=request.user.id)
    notice=models.Notice.objects.all()
    mydict={
        'salary':teacherdata[0].salary,
        'mobile':teacherdata[0].mobile,
        'date':teacherdata[0].joindate,
        'notice':notice
    }
    return render(request,'school/teacher_dashboard.html',context=mydict)



@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_attendance_view(request):
    return render(request,'school/teacher_attendance.html')


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_take_attendance_view(request, cl):
    students = models.StudentExtra.objects.filter(cl=cl)
    if request.method == 'POST':
        date = request.POST.get('date')
        for student in students:
            status = request.POST.get(f'present_status_{student.id}')
            if status:  # Ensure checkbox selected
                attendance = models.Attendance()
                attendance.cl = cl
                attendance.date = date
                attendance.roll = student.roll
                attendance.present_status = status
                attendance.save()
        return redirect('teacher-attendance')
    
    return render(request, 'school/teacher_take_attendance.html', {'students': students})


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_attendance_view(request,cl):
    form=forms.AskDateForm()
    if request.method=='POST':
        form=forms.AskDateForm(request.POST)
        if form.is_valid():
            date=form.cleaned_data['date']
            attendancedata=models.Attendance.objects.all().filter(date=date,student__cl=cl)
            studentdata=models.StudentExtra.objects.all().filter(student__cl=cl)
            mylist=zip(attendancedata,studentdata)
            return render(request,'school/teacher_view_attendance_page.html',{'cl':cl,'mylist':mylist,'date':date})
        else:
            print('form invalid')
    return render(request,'school/teacher_view_attendance_ask_date.html',{'cl':cl,'form':form})



@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_notice_view(request):
    form=forms.NoticeForm()
    if request.method=='POST':
        form=forms.NoticeForm(request.POST)
        if form.is_valid():
            form=form.save(commit=False)
            form.by=request.user.first_name
            form.save()
            return redirect('teacher-dashboard')
        else:
            print('form invalid')
    return render(request,'school/teacher_notice.html',{'form':form})







#FOR STUDENT AFTER THEIR Loginnnnnnnnnnnnnnnnnnnnn
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    studentdata=models.StudentExtra.objects.all().filter(status=True,user_id=request.user.id)
    notice=models.Notice.objects.all()
    mydict={
        'roll':studentdata[0].roll,
        'mobile':studentdata[0].mobile,
        'fee':studentdata[0].fee,
        'notice':notice
    }
    return render(request,'school/student_dashboard.html',context=mydict)



@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_attendance_view(request):
    form=forms.AskDateForm()
    if request.method=='POST':
        form=forms.AskDateForm(request.POST)
        if form.is_valid():
            date=form.cleaned_data['date']
            studentdata=models.StudentExtra.objects.all().filter(user_id=request.user.id,status=True)
            attendancedata=models.Attendance.objects.all().filter(date=date,cl=studentdata[0].cl,roll=studentdata[0].roll)
            mylist=zip(attendancedata,studentdata)
            return render(request,'school/student_view_attendance_page.html',{'mylist':mylist,'date':date})
        else:
            print('form invalid')
    return render(request,'school/student_view_attendance_ask_date.html',{'form':form})









# for aboutus and contact ussssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss
def aboutus_view(request):
    return render(request,'school/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message,settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'school/contactussuccess.html')
    return render(request, 'school/contactus.html', {'form':sub})





# for payment using Razorpayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
# Updated pay_view with student_id
# Payment Page View — creates Razorpay Order
def pay_view(request, student_id):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    payment = client.order.create({
        "amount": 10000,  # ₹100 in paise
        "currency": "INR",
        "payment_capture": "1"
    })

    context = {
        'payment': payment,                 # Razorpay order dict
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'student_id': student_id           # Passed to HTML & backend
    }

    return render(request, 'school/payment.html', context)

#  Razorpay Callback View — handle payment successssssssssssssssssssssssssssss

@csrf_exempt  # CSRF disabled for JS fetch()
def payment_success(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)

        student_id = data.get("student_id")
        payment_id = data.get("payment_id")
        order_id = data.get("order_id")

        # For testing: print to console or save to DB
        print(" Payment Success!")
        print("Student ID:", student_id)
        print("Payment ID:", payment_id)
        print("Order ID:", order_id)

        # Optional: Save to DB (not shown here)

        return JsonResponse({
            "status": "Payment Successful",
            "student_id": student_id
        })

    return JsonResponse({"error": "Invalid request"}, status=400)


#student-attendance export pdffffffffffffffffffffffffffffffffffffffffffffff
def export_attendance_pdf(request):
    students = StudentExtra.objects.all()  # or filter by class/date
    template_path = 'school/attendance_pdf.html'
    context = {'students': students}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="attendance_report.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors with PDF generation <pre>' + html + '</pre>')
    return response


# calender view for all student,teacherrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr
def calendar_view(request):
    return render(request, 'school/calendar.html')

def get_events(request):
    events = Event.objects.all()
    event_list = []
    for event in events:
        event_list.append({
            "title": event.title,
            "start": event.start_time.isoformat(),
            "end": event.end_time.isoformat(),
        })
    return JsonResponse(event_list, safe=False)

