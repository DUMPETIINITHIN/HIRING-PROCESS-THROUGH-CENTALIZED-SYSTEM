from django.contrib import admin
from .models import signup
# Register your models here.
admin.site.register(signup)
from .models import Applicant, Interview, AccessLog, JobListing
admin.site.register(Applicant)
admin.site.register(Interview)
admin.site.register(AccessLog)
admin.site.register(JobListing)
