from django.contrib import messages
from django.contrib.auth import login, authenticate, get_user_model, logout as auth_logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from .models import CarOwner, Usertable
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from social_django.models import UserSocialAuth
from django.contrib.auth.hashers import make_password
from django.urls import reverse
def booking(request):
    return render(request, "booking.html")

def index(request):
    return render(request, "index.html")

def signup(request):
    if request.method == 'POST':
        role = request.POST['role']
        firstname = request.POST['fname']
        email = request.POST['email']
        lastname = request.POST['lname']
        dob = request.POST['dob']
        password = request.POST['password']
        phone = request.POST['phone']
        user = Usertable(
            first_name=firstname,
            last_name=lastname,
            role=role,
            dob=dob,
            email=email,
            phone=phone
        )
        user.set_password(password)
        user.save()
        return redirect('user_login')
    return render(request, "registration.html")

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Attempt to authenticate as a Usertable user
            user = Usertable.objects.get(email=email)
            if user.is_active and check_password(password, user.password):
                request.session['email'] = email
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                # Check the user's role
                if user.role == 'car_owner':
                    # Redirect to 'index3' if the user is a car owner
                    return redirect('index3')
                elif user.is_superuser:
                    # Redirect the superuser (admin) to 'adminreg'
                    return redirect('adminreg')
                else:
                    return redirect('index2')

        except Usertable.DoesNotExist:
            pass  # User not found in Usertable, continue to check CarOwner

        try:
            # Attempt to authenticate as a CarOwner user
            car_owner = CarOwner.objects.get(email=email)
            if check_password(password, car_owner.password):
                request.session['email'] = email

                # You can check for proposal_status or any other condition specific to CarOwner here
                # For example, if car_owner.proposal_status == 'Accepted', redirect to a specific view

                return redirect('index3')  # Redirect to the car owner's page

        except CarOwner.DoesNotExist:
            # Neither Usertable nor CarOwner user found
            error_message = "Invalid credentials"
            messages.error(request, error_message)

    response = render(request, 'login.html')
    response['Cache-Control'] = 'no-store, must-revalidate'
    return response
def logout(request):
    auth_logout(request)
    return redirect('index')


def index2(request):
    if 'email'or 'usename' in request.session:  # Correct the check for session variable
        response = render(request, 'index2.html')
        response['Cache-Control'] = 'no-store, must-revalidate'
        return response
    else:
        return redirect('index')

def check_user_exists(request):
    email = request.GET.get('email')
    data = {
        'exists': Usertable.objects.filter(email=email).exists()
    }
    return JsonResponse(data)

from .models import CarOwner

def adminreg(request):
    if request.method == 'POST':
        for user in Usertable.objects.exclude(is_superuser=True):
            status_field_name = f'user_status_{user.email}'
            user_status = request.POST.get(status_field_name, '')

            if user_status == 'on':
                if not user.is_active:
                    user.is_active = True
                    user.save()
                    send_activation_email(user)
                else:
                    continue  # Skip the rest of the loop if the user is already active
            else:
                if user.is_active:
                    user.is_active = False
                    user.save()
                    send_deactivation_email(user)
                else:
                    continue  # Skip the rest of the loop if the user is already inactive

        for carowner in CarOwner.objects.all():
            status_field_name = f'proposal_status_{carowner.email}'
            proposal_status = request.POST.get(status_field_name, 'Pending')

            if proposal_status == 'Accepted' and carowner.proposal_status != 'Accepted':
                # Generate a random password for the car owner
                import random
                import string
                password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
                # Set the hashed password for the CarOwner
                carowner.password = make_password(password)
                carowner.save()
                
                # Send an email to the car owner with their password
                send_password_email(carowner, password)
                send_proposal_notification(carowner, proposal_status)
            elif proposal_status != 'Accepted':
                # Reset the password_generated flag if the proposal status is not 'Accepted'
                carowner.password_generated = False
                carowner.save()

            carowner.proposal_status = proposal_status
            carowner.save()

    admin_users = Usertable.objects.filter(role='admin')
    normal_users = Usertable.objects.filter(role='normal_user')
    club_users = Usertable.objects.filter(role='club_user')

    car_owners = CarOwner.objects.all()

    context = {
        'admin_users': admin_users,
        'normal_users': normal_users,
        'club_users': club_users,
        'car_owners': car_owners,
    }

    return render(request, 'adminreg.html', context)


def send_password_email(carowner, password):
    subject = 'Your Password for Wheelways Account'
    message = f'Your password for your Wheelways account is: {password}'
    from_email = 'wheelways2@gmail.com'  # Update with your email
    recipient_list = [carowner.email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

def send_activation_email(user):
    send_mail(
        'Account Activation',
        'Your account has been activated. You can now log in and access your account.',
        'wheelways2@gmail.com',  # Replace with your email address
        [user.email],
        fail_silently=False,
    )

def send_deactivation_email(user):
    send_mail(
        'Account Deactivation',
        'Your account has been deactivated. Please contact the admin for more information.',
        'wheelways2@gmail.com',  # Replace with your email address
        [user.email],
        fail_silently=False,
    )


def user_profile(request):
    user = request.user
    formatted_dob = user.dob.strftime('%Y-%m-%d') if user.dob else ''
    context = {'user': user, 'formatted_dob': formatted_dob}
    return render(request, 'userprofile.html', context)

def update_user_details(request):
    if request.method == 'POST':
        new_dob = request.POST.get('new_dob')
        new_first_name = request.POST.get('new_first_name')
        new_last_name = request.POST.get('new_last_name')
        new_phone_number = request.POST.get('new_phone')  # Add this line

        # Update the user's details in the database
        user = request.user
        user.dob = new_dob
        user.first_name = new_first_name
        user.last_name = new_last_name
        user.phone = new_phone_number  # Add this line
        user.save()

        messages.success(request, 'User details updated successfully.')
        return redirect('user_profile')  # Redirect to the user profile page

    return render(request, 'userprofile.html')
def owners(request):
    return render(request, "owners.html")

def google_authenticate(request):
    # Handle the Google OAuth2 authentication process
    # ...

    # After successful authentication, create or get the user
    try:
        user_social = UserSocialAuth.objects.get(provider='google-oauth2', user=request.user)
        user = user_social.user
    except UserSocialAuth.DoesNotExist:
        user = request.user

    # Set the user's role to "user"
        user.role = 'normal_users'
        user.save()

    # Set the user's is_user field to True
        user.is_normal_user = True
        user.save()

    
    return redirect('index2')  
def owners(request):
    if request.method == 'POST':
        venue_name = request.POST.get('venue_name')
        email = request.POST.get('email')
        contact_number = request.POST.get('contact_number')
        document = request.FILES['document']
        address = request.POST.get('address')
        location = request.POST.get('location') 

        # Create an instance of the Owners model and save it
        owner = CarOwner(  # Use a different variable name (owner) for the instance
            venue_name=venue_name,
            email=email,
            contact_number=contact_number,
            document=document,
            address=address,
            location=location
        )
        owner.save()

        # Redirect to a success page or do something else
        return redirect('index')  # Change 'index' to the appropriate URL

    return render(request, 'owners.html')
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from .models import CarOwner

def download_pdf(request, car_owner_email):
    car_owner = get_object_or_404(CarOwner, email=car_owner_email)
    pdf_file = car_owner.document
    response = FileResponse(pdf_file)
    response['Content-Disposition'] = f'attachment; filename="{car_owner.venue_name}.pdf"'
    return response
def send_proposal_notification(carowner, proposal_status):
    subject = f'Proposal Status Update for {carowner.venue_name}'
    message = f'Your proposal for {carowner.venue_name} has been {proposal_status.lower()}.'
    from_email = 'wheelways2@gmail.com'  # Update with your email
    recipient_list = [carowner.email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

def index3(request):
    # This is a sample view for the 'index3' page for car owners.
    # You can customize this view as per your requirements.
    return render(request, 'index3.html')
def addcar(request):
    # This is a sample view for the 'index3' page for car owners.
    # You can customize this view as per your requirements.
    return render(request, 'addcar.html')
