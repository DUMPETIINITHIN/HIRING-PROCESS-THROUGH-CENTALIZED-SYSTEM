from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import signup as SignupModel, Applicant, Interview, AccessLog, CandidateStatus, JobListing, InterviewSchedule

# Helper function to get client IP
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Create your views here.
def home(request):
    return render(request, "index.html")

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return render(request, "login.html", {"error": "Please enter both username and password."})

        # Simple authentication against SignupModel (stored passwords are plaintext)
        try:
            user = SignupModel.objects.get(username=username)
            if user.password == password:
                # store user id in session so dashboard/profile can show logged-in user
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                # also store role in session for quick checks in templates/views
                request.session['role'] = user.role
                # Redirect to dashboard
                return redirect('dashboard')
            else:
                return render(request, "login.html", {"error": "Invalid username or password."})
        except SignupModel.DoesNotExist:
            return render(request, "login.html", {"error": "User not found. Please sign up first."})

    return render(request, "login.html")


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username') 
        email = request.POST.get('email')
        phone = request.POST.get('phone_number') 
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')

        if not all([username, email, phone, password, confirm_password, role]):
            return render(request, "signup.html", {"error": "Please fill all fields."})

        if password != confirm_password:
            return render(request, "signup.html", {"error": "Passwords do not match."})

        # Check if email already exists
        if SignupModel.objects.filter(email=email).exists():
            return render(request, "signup.html", {"error": "Email already exists. Please use a different email or login."})

        try:
            # Save to database
            user = SignupModel(
                username=username,
                email=email,
                phone_number=phone,
                password=password,
                confirm_password=confirm_password,
                role=role,
            )
            user.save()

            # After successful signup redirect to login page
            return redirect('login')
        except Exception as e:
            return render(request, "signup.html", {"error": f"Error during signup: {str(e)}"})

    return render(request, "signup.html")


def dashboard(request):
    # determine logged-in user (from session) if any
    user_obj = None
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user_obj = SignupModel.objects.get(id=user_id)
        except SignupModel.DoesNotExist:
            user_obj = None

    # summary counts for dashboard
    total_applicants = Applicant.objects.count()
    shortlisted_count = Applicant.objects.filter(status='Shortlisted').count()
    interviews_count = Interview.objects.count()
    selected_count = Applicant.objects.filter(status='Selected').count()
    recent_applicants = Applicant.objects.all().order_by('-created_at')[:5]
    context = {
        'applicants_count': total_applicants,
        'shortlisted_count': shortlisted_count,
        'interviews_count': interviews_count,
        'selected_count': selected_count,
        'recent_applicants': recent_applicants,
        'name': user_obj.username if user_obj else None,
        'email': user_obj.email if user_obj else None,
        'user_role': user_obj.role if user_obj else 'Guest',
    }
    return render(request, "dashboard.html", context)


from django.shortcuts import render, redirect
from .models import signup as SignupModel, Applicant, Interview

def profile(request):
    user_obj = None
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user_obj = SignupModel.objects.get(id=user_id)
        except SignupModel.DoesNotExist:
            user_obj = None

    if request.method == 'POST':
        if not user_obj:
            return redirect('login')

        new_username = request.POST.get('username')
        new_email = request.POST.get('email')
        new_phone = request.POST.get('phone_number')
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # validate
        error = None
        if not new_username or not new_email:
            error = 'Name and email are required.'
        elif new_password and new_password != confirm_password:
            error = 'Passwords do not match.'
        elif SignupModel.objects.filter(email=new_email).exclude(id=user_obj.id).exists():
            error = 'Email already in use by another account.'

        if error:
            # re-render with error + recent data
            return render(request, 'profile.html', {
                'name': user_obj.username,
                'email': user_obj.email,
                'user': user_obj,
                'applicants_count': Applicant.objects.count(),
                'interviews_count': Interview.objects.count(),
                'selected_count': Applicant.objects.filter(status='Selected').count(),
                'recent_applicants': Applicant.objects.all().order_by('-created_at')[:5],
                'recent_interviews': Interview.objects.select_related('applicant').all().order_by('-interview_date','-interview_time')[:5],
                'error': error,
            })

        # persist to DB
        user_obj.username = new_username
        user_obj.email = new_email
        user_obj.phone_number = new_phone or user_obj.phone_number
        if new_password:
            user_obj.password = new_password
            user_obj.confirm_password = new_password
        user_obj.save()
        request.session['username'] = user_obj.username

        return render(request, 'profile.html', {
            'name': user_obj.username,
            'email': user_obj.email,
            'user': user_obj,
            'applicants_count': Applicant.objects.count(),
            'interviews_count': Interview.objects.count(),
            'selected_count': Applicant.objects.filter(status='Selected').count(),
            'recent_applicants': Applicant.objects.all().order_by('-created_at')[:5],
            'recent_interviews': Interview.objects.select_related('applicant').all().order_by('-interview_date','-interview_time')[:5],
            'success': 'Profile updated successfully.'
        })

    # GET: show profile
    context = {
        'name': user_obj.username if user_obj else 'Admin',
        'email': user_obj.email if user_obj else 'admin@example.com',
        'user': user_obj,
        'applicants_count': Applicant.objects.count(),
        'interviews_count': Interview.objects.count(),
        'selected_count': Applicant.objects.filter(status='Selected').count(),
        'recent_applicants': Applicant.objects.all().order_by('-created_at')[:5],
        'recent_interviews': Interview.objects.select_related('applicant').all().order_by('-interview_date','-interview_time')[:5],
    }
    # compute initials for avatar (first letters of up to two name parts)
    name_for_initials = (user_obj.username if user_obj else 'Admin')
    parts = [p for p in name_for_initials.split() if p]
    if len(parts) == 0:
        initials = ''
    elif len(parts) == 1:
        initials = parts[0][0]
    else:
        initials = parts[0][0] + parts[1][0]
    initials = initials.upper()
    context['initials'] = initials
    return render(request, 'profile.html', context)


def logout_view(request):
    # clear session and redirect to login
    request.session.flush()
    return redirect('login')
def applicants(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        position = request.POST.get('position')
        status = request.POST.get('status') or 'Reviewing'
        resume_file = request.FILES.get('resume')

        if not all([name, email]):
            applicants_qs = Applicant.objects.all().order_by('-created_at')
            return render(request, 'applicants.html', {'applicants': applicants_qs, 'error': 'Name and email are required.'})

        Applicant.objects.create(
            name=name,
            email=email,
            phone=phone,
            position=position,
            status=status,
            resume=resume_file
        )

        return redirect('applicants')

    applicants_qs = Applicant.objects.all().order_by('-created_at')
    return render(request, 'applicants.html', {'applicants': applicants_qs})
def interviews(request):
    if request.method == 'POST':
        applicant_id = request.POST.get('applicant_id')
        interview_date = request.POST.get('interview_date')
        interview_time = request.POST.get('interview_time')
        interview_mode = request.POST.get('interview_mode')
        notes = request.POST.get('notes', '')

        if not all([applicant_id, interview_date, interview_time, interview_mode]):
            all_applicants = Applicant.objects.all().order_by('-created_at')
            interviews_list = Interview.objects.all().order_by('-interview_date')
            return render(request, 'interviews.html', {
                'applicants': all_applicants,
                'interviews': interviews_list,
                'error': 'Please fill all required fields.'
            })

        try:
            applicant = Applicant.objects.get(id=applicant_id)
            interview = Interview.objects.create(
                applicant=applicant,
                interview_date=interview_date,
                interview_time=interview_time,
                interview_mode=interview_mode,
                status='Scheduled',
                notes=notes
            )
            # Update applicant status
            if applicant.status != 'Interview Scheduled':
                applicant.status = 'Interview Scheduled'
                applicant.save()
            return redirect('interviews')
        except Applicant.DoesNotExist:
            applicants_qs = Applicant.objects.all().order_by('-created_at')
            interviews_list = Interview.objects.all().order_by('-interview_date')
            return render(request, 'interviews.html', {
                'applicants': applicants_qs,
                'interviews': interviews_list,
                'error': 'Selected applicant not found.'
            })

    # Get all applicants (not just shortlisted)
    all_applicants = Applicant.objects.all().order_by('-created_at')
    # Get all scheduled interviews
    interviews_list = Interview.objects.all().order_by('-interview_date')
    return render(request, 'interviews.html', {'applicants': all_applicants, 'interviews': interviews_list})

def selected(request):
    # Check if user is logged in and is HR
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    
    try:
        user_obj = SignupModel.objects.get(id=user_id)
    except SignupModel.DoesNotExist:
        return redirect('login')
    
    # Only HR users can access this page (case-insensitive check).
    # Allow role to be validated from the DB or from the session as a fallback.
    session_role = (request.session.get('role') or '').strip().upper()
    user_role_upper = (user_obj.role or '').strip().upper()
    if user_role_upper != 'HR' and session_role != 'HR':
        # Log access denial attempt
        AccessLog.objects.create(
            user=user_obj,
            username=user_obj.username,
            user_role=user_obj.role,
            attempted_page='Selected Applicants',
            access_granted=False,
            ip_address=get_client_ip(request)
        )
        # Get recent access attempts
        recent_attempts = AccessLog.objects.filter(user=user_obj).order_by('-timestamp')[:5]
        return render(request, 'access_denied.html', {
            'message': 'You do not have access to this page. Only HR users can access the selected applicants page.',
            'recent_attempts': recent_attempts,
            'user': user_obj
        })
    
    # Log successful access
    AccessLog.objects.create(
        user=user_obj,
        username=user_obj.username,
        user_role=user_obj.role,
        attempted_page='Selected Applicants',
        access_granted=True,
        ip_address=get_client_ip(request)
    )
    
    if request.method == 'POST':
        applicant_id = request.POST.get('applicant_id')
        try:
            applicant = Applicant.objects.get(id=applicant_id)
            applicant.status = 'Selected'
            applicant.save()
            # update/create candidate status for the user with matching email
            try:
                candidate_user = SignupModel.objects.filter(email=applicant.email).first()
                if candidate_user:
                    CandidateStatus.objects.update_or_create(
                        candidate=candidate_user,
                        defaults={
                            'current_status': 'Selected',
                            'applicant': applicant,
                            'position_applied': applicant.position,
                            'selection_message': f'Congratulations {applicant.name}, you have been selected for {applicant.position}.'
                        }
                    )
            except Exception:
                # don't block the flow if updating CandidateStatus fails
                pass

            return redirect('selected')
        except Applicant.DoesNotExist:
            pass

    selected_applicants = Applicant.objects.filter(status='Selected').order_by('-created_at')
    interview_scheduled = Applicant.objects.filter(status='Interview Scheduled').order_by('-created_at')
    return render(request, 'selected.html', {'selected_applicants': selected_applicants, 'applicants': interview_scheduled})

def rejected(request):
    # Check if user is logged in and is HR
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    
    try:
        user_obj = SignupModel.objects.get(id=user_id)
    except SignupModel.DoesNotExist:
        return redirect('login')
    
    # Only HR users can access this page (case-insensitive check).
    # Allow role to be validated from the DB or from the session as a fallback.
    session_role = (request.session.get('role') or '').strip().upper()
    user_role_upper = (user_obj.role or '').strip().upper()
    if user_role_upper != 'HR' and session_role != 'HR':
        # Log access denial attempt
        AccessLog.objects.create(
            user=user_obj,
            username=user_obj.username,
            user_role=user_obj.role,
            attempted_page='Rejected Applicants',
            access_granted=False,
            ip_address=get_client_ip(request)
        )
        # Get recent access attempts
        recent_attempts = AccessLog.objects.filter(user=user_obj).order_by('-timestamp')[:5]
        return render(request, 'access_denied.html', {
            'message': 'You do not have access to this page. Only HR users can access the rejected applicants page.',
            'recent_attempts': recent_attempts,
            'user': user_obj
        })
    
    # Log successful access
    AccessLog.objects.create(
        user=user_obj,
        username=user_obj.username,
        user_role=user_obj.role,
        attempted_page='Rejected Applicants',
        access_granted=True,
        ip_address=get_client_ip(request)
    )
    
    if request.method == 'POST':
        applicant_id = request.POST.get('applicant_id')
        reason = request.POST.get('reason', '')
        try:
            applicant = Applicant.objects.get(id=applicant_id)
            applicant.status = 'Rejected'
            applicant.save()
            # update/create candidate status for the user with matching email
            try:
                candidate_user = SignupModel.objects.filter(email=applicant.email).first()
                if candidate_user:
                    CandidateStatus.objects.update_or_create(
                        candidate=candidate_user,
                        defaults={
                            'current_status': 'Rejected',
                            'applicant': applicant,
                            'position_applied': applicant.position,
                            'selection_message': reason or f'Sorry {applicant.name}, your application for {applicant.position} was not successful.'
                        }
                    )
            except Exception:
                pass

            return redirect('rejected')
        except Applicant.DoesNotExist:
            pass

    rejected_applicants = Applicant.objects.filter(status='Rejected').order_by('-created_at')
    interview_scheduled = Applicant.objects.filter(status='Interview Scheduled').order_by('-created_at')
    return render(request, 'rejected.html', {'rejected_applicants': rejected_applicants, 'applicants': interview_scheduled})

from .models import JobListing    
def joblisting(request):
    jobs = JobListing.objects.all()
    
    if request.method == 'POST':
        keyword = request.POST.get('keyword', '')
        location = request.POST.get('location', '')
        job_type = request.POST.get('type', '')
        
        if keyword:
            jobs = jobs.filter(title__icontains=keyword)
        if location:
            jobs = jobs.filter(location=location)
        if job_type:
            jobs = jobs.filter(job_type=job_type)
    
    return render(request, 'joblisting.html', {'jobs': jobs})

def interview(request):
    from .models import InterviewSchedule, JobListing
    
    interviews = InterviewSchedule.objects.all()
    jobs = JobListing.objects.all()
    
    if request.method == 'POST':
        # Check if it's a form submission for creating an interview
        if 'candidate_name' in request.POST:
            candidate_name = request.POST.get('candidate_name', '').strip()
            candidate_email = request.POST.get('candidate_email', '').strip()
            candidate_phone = request.POST.get('candidate_phone', '').strip()
            job_title_id = request.POST.get('job_title', '')
            interview_type = request.POST.get('interview_type', '')
            interview_date = request.POST.get('interview_date', '')
            interview_time = request.POST.get('interview_time', '')
            interviewer_name = request.POST.get('interviewer_name', '').strip()
            interviewer_email = request.POST.get('interviewer_email', '').strip()
            location = request.POST.get('location', '').strip()
            notes = request.POST.get('notes', '').strip()
            
            if job_title_id and candidate_name and candidate_email and interview_date and interview_time:
                try:
                    job_title = JobListing.objects.get(id=job_title_id)
                    InterviewSchedule.objects.create(
                        candidate_name=candidate_name,
                        candidate_email=candidate_email,
                        candidate_phone=candidate_phone,
                        job_title=job_title,
                        interview_type=interview_type,
                        interview_date=interview_date,
                        interview_time=interview_time,
                        interviewer_name=interviewer_name,
                        interviewer_email=interviewer_email,
                        location=location,
                        notes=notes,
                        status='scheduled'
                    )
                except JobListing.DoesNotExist:
                    pass
        
        # Check if it's a filter request
        status = request.POST.get('status', '').strip()
        interview_type = request.POST.get('interview_type', '').strip()
        
        if status:
            interviews = interviews.filter(status=status)
        if interview_type:
            interviews = interviews.filter(interview_type=interview_type)
    
    return render(request, 'interviewschedule.html', {'interviews': interviews, 'jobs': jobs})


def reports(request):
    """Reports page for candidates to see their application status"""
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    
    try:
        user_obj = SignupModel.objects.get(id=user_id)
    except SignupModel.DoesNotExist:
        return redirect('login')
    
    # Only candidates can access reports
    if user_obj.role != 'Candidate':
        return render(request, 'access_denied.html', {
            'message': 'Reports are only available for candidates. HR can view selection/rejection pages instead.'
        })
    
    # Get candidate status
    candidate_status = None
    try:
        candidate_status = CandidateStatus.objects.get(candidate=user_obj)
    except CandidateStatus.DoesNotExist:
        # Create status if doesn't exist
        candidate_status = CandidateStatus.objects.create(candidate=user_obj)
    
    # Get related interview data
    interviews = []
    if candidate_status.applicant:
        interviews = Interview.objects.filter(applicant=candidate_status.applicant).order_by('-interview_date')
    
    # Determine message based on status
    status_message = ""
    message_type = "info"
    
    if candidate_status.current_status == 'Applied':
        status_message = "Your application has been received. We are reviewing your profile."
        message_type = "info"
    elif candidate_status.current_status == 'Reviewing':
        status_message = "Your application is under review. We will contact you shortly."
        message_type = "info"
    elif candidate_status.current_status == 'Shortlisted':
        status_message = "🎉 Congratulations! You are shortlisted for the interview."
        message_type = "success"
    elif candidate_status.current_status == 'Interview Scheduled':
        status_message = "✅ Your interview has been scheduled. Please check the details below."
        message_type = "success"
    elif candidate_status.current_status == 'Selected':
        status_message = "🏆 Congratulations! You have been selected. We will be in touch soon."
        message_type = "success"
    elif candidate_status.current_status == 'Rejected':
        status_message = "Thank you for your interest. Unfortunately, you were not selected for this position."
        message_type = "danger"
    
    context = {
        'user': user_obj,
        'candidate_status': candidate_status,
        'interviews': interviews,
        'status_message': status_message,
        'message_type': message_type,
    }
    
    return render(request, 'reports.html', context)