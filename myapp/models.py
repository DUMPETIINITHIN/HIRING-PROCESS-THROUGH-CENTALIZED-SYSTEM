from django.db import models

# Create your models here.
class signup(models.Model):
    ROLE_CHOICES = [
        ('Candidate', 'Candidate'),
        ('HR', 'HR'),
    ]
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=10)
    password = models.CharField(max_length=100)
    confirm_password = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Candidate')


class Applicant(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    # Resume file (optional)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    position = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=50, default='Reviewing')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.position}"


class Interview(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='interviews')
    interview_date = models.DateField()
    interview_time = models.TimeField()
    interview_mode = models.CharField(max_length=50, choices=[('Online', 'Online'), ('Offline', 'Offline')])
    status = models.CharField(max_length=50, default='Scheduled', choices=[
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('No Show', 'No Show')
    ])
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interview - {self.applicant.name} on {self.interview_date}"

    class Meta:
        ordering = ['-interview_date', '-interview_time']


class AccessLog(models.Model):
    """Track access denial attempts"""
    user = models.ForeignKey(signup, on_delete=models.CASCADE, related_name='access_logs', null=True, blank=True)
    username = models.CharField(max_length=100)
    user_role = models.CharField(max_length=20)
    attempted_page = models.CharField(max_length=100)
    access_granted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)

    def __str__(self):
        status = "Granted" if self.access_granted else "Denied"
        return f"{self.username} ({self.user_role}) - {self.attempted_page} - {status}"

    class Meta:
        ordering = ['-timestamp']


class CandidateStatus(models.Model):
    """Track candidate application progress for reporting"""
    STATUS_CHOICES = [
        ('Applied', 'Applied'),
        ('Reviewing', 'Reviewing'),
        ('Shortlisted', 'Shortlisted'),
        ('Interview Scheduled', 'Interview Scheduled'),
        ('Selected', 'Selected'),
        ('Rejected', 'Rejected'),
    ]
    candidate = models.OneToOneField(signup, on_delete=models.CASCADE, related_name='status_report')
    applicant = models.OneToOneField(Applicant, on_delete=models.CASCADE, related_name='candidate_status', null=True, blank=True)
    current_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Applied')
    position_applied = models.CharField(max_length=150, blank=True)
    applied_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    interview_scheduled = models.BooleanField(default=False)
    interview_date = models.DateField(null=True, blank=True)
    interview_time = models.TimeField(null=True, blank=True)
    interview_mode = models.CharField(max_length=50, blank=True)
    interview_notes = models.TextField(blank=True)
    selection_message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.candidate.username} - {self.current_status}"

    class Meta:
        ordering = ['-last_updated']

class JobListing(models.Model):
    JOB_TYPE_CHOICES = [
        ('full-time', 'Full-Time'),
        ('part-time', 'Part-Time'),
        ('internship', 'Internship'),
    ]
    
    LOCATION_CHOICES = [
        ('hyderabad', 'Hyderabad'),
        ('bangalore', 'Bangalore'),
        ('chennai', 'Chennai'),
        ('mumbai', 'Mumbai'),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def _str_(self):
        return self.title

class InterviewSchedule(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    INTERVIEW_TYPE_CHOICES = [
        ('technical', 'Technical'),
        ('hr', 'HR'),
        ('general', 'General'),
        ('final', 'Final Round'),
    ]
    
    candidate_name = models.CharField(max_length=100)
    candidate_email = models.EmailField()
    candidate_phone = models.CharField(max_length=15)
    job_title = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='interviews')
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPE_CHOICES)
    interview_date = models.DateField()
    interview_time = models.TimeField()
    interviewer_name = models.CharField(max_length=100)
    interviewer_email = models.EmailField()
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-interview_date', '-interview_time']
    
    def _str_(self):
        return f"{self.candidate_name} - {self.job_title} - {self.interview_date}"

class InterviewSchedule(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    INTERVIEW_TYPE_CHOICES = [
        ('technical', 'Technical'),
        ('hr', 'HR'),
        ('general', 'General'),
        ('final', 'Final Round'),
    ]
    
    candidate_name = models.CharField(max_length=100)
    candidate_email = models.EmailField()
    candidate_phone = models.CharField(max_length=15)
    job_title = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='interviews')
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPE_CHOICES)
    interview_date = models.DateField()
    interview_time = models.TimeField()
    interviewer_name = models.CharField(max_length=100)
    interviewer_email = models.EmailField()
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-interview_date', '-interview_time']
    
    def _str_(self):
        return f"{self.candidate_name} - {self.job_title} - {self.interview_date}"