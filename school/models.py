from django.db import models
from django.contrib.auth.models import User

from django.utils.text import slugify


# Create your models here.
# -------------------------------
#  PROFILE MODEL (for teachers, toppers, etc.)
# -------------------------------
class Profile(models.Model):
    CATEGORY_CHOICES = [
        ('teacher', 'Teacher'),
        ('10th_topper', '10th Topper'),
        ('12th_topper', '12th Topper'),
        ('best_in_class', 'Best in Class'),
    ]

    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    experience = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='profiles/')
    bio = models.TextField()
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category})"


###
# -------------------------------
#  DEPARTMENTS for Teachers
# -------------------------------

DEPARTMENTS = [
    ('Maths', 'Mathematics'),
    ('Science', 'Science'),
    ('English', 'English'),
    ('Hindi', 'Hindi'),
    ('Social', 'Social Science'),
    ('Computer','computer'),
    ('physics','physics'),
    ('chemistry','chemistry'),
    ('biology','biology'),
]


class TeacherExtra(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    salary = models.PositiveIntegerField(null=False)
    joindate=models.DateField(auto_now_add=True)
    mobile = models.CharField(max_length=40)
    department = models.CharField(max_length=200, choices=DEPARTMENTS)
    status=models.BooleanField(default=False)
    def __str__(self):
        return self.user.first_name
    @property
    def get_id(self):
        return self.user.id
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name


# -------------------------------
#  STUDENT MODEL
# -------------------------------

classes=[('one','one'),('two','two'),('three','three'),
('four','four'),('five','five'),('six','six'),('seven','seven'),('eight','eight'),('nine','nine'),('ten','ten'),('eleven','eleven'),('twelve','twelve')]
class StudentExtra(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    roll = models.CharField(max_length=10)
    mobile = models.CharField(max_length=40,null=True)
    fee=models.PositiveIntegerField(null=True)
    cl= models.CharField(max_length=10,choices=classes,default='one')
    status=models.BooleanField(default=False)

    admission_date = models.DateField(auto_now_add=True)

    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return self.user.first_name

# -------------------------------
#  ATTENDANCE MODEL (Final)
# -------------------------------


class Attendance(models.Model):
    student = models.ForeignKey('StudentExtra', on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10)  # Present or Absent

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"
        return f"{self.student.user.get_full_name()} - {self.date} - {self.status}"


# -------------------------------
#  NOTICE MODEL
# -------------------------------


class Notice(models.Model):
    date=models.DateField(auto_now=True)
    by=models.CharField(max_length=20,null=True,default='school')
    message=models.CharField(max_length=500)


# calender model for teacher ,studentttttttttttttttttttttttttttttttttttt
class Event(models.Model):
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.title


