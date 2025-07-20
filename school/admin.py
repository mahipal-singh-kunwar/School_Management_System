from django.contrib import admin
from .models import Attendance, StudentExtra, TeacherExtra, Notice
from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'category']
    list_filter = ['category']

admin.site.register(Profile, ProfileAdmin)





#  Customize StudentExtra admin
class StudentExtraAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'roll', 'mobile', 'fee', 'cl', 'status']
    list_editable = ['status']
    search_fields = ['user__first_name', 'user__last_name', 'roll', 'cl']
    list_filter = ['cl', 'status']

admin.site.register(StudentExtra, StudentExtraAdmin)


#  Customize TeacherExtra admin
class TeacherExtraAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'mobile', 'salary', 'joindate', 'department', 'status']
    list_editable = ['department', 'status']
    search_fields = ['user__first_name', 'user__last_name', 'department']
    list_filter = ['department', 'status']

admin.site.register(TeacherExtra, TeacherExtraAdmin)


# # Customize Attendance admin (corrected version)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['get_student_name', 'get_student_id', 'get_student_class', 'date', 'status']
    list_filter = ['date', 'status']
    search_fields = ['student__name', 'student__student_id', 'student__cls']

    def get_student_name(self, obj):
        return obj.student.name
    get_student_name.short_description = 'Student Name'

    def get_student_id(self, obj):
        return obj.student.student_id
    get_student_id.short_description = 'Student ID'

    def get_student_class(self, obj):
        return obj.student.cls
    get_student_class.short_description = 'Class'

# Register Attendance with custom admin
admin.site.register(Attendance, AttendanceAdmin)



#  Customize Notice admin
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['date', 'by', 'message']
    search_fields = ['by', 'message']
    list_filter = ['date', 'by']

admin.site.register(Notice, NoticeAdmin)
