from django.contrib import messages
from django.contrib.auth import login, authenticate, get_user_model, logout as auth_logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from .models import CarImage, CarOwner, Usertable
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from social_django.models import UserSocialAuth
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.shortcuts import render, redirect
from .models import Booking  # Import your actual model
from django.http import HttpResponse


def booking(request, car_id,car_owner_id, user_id):
    car_id = car_id
    owner = get_object_or_404(CarOwner, venue_name=car_owner_id)
    client=user_id
    if request.method == 'POST':
        # Extract form data from request.POST
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile_number = request.POST.get('mobile_number')
        license_number = request.POST.get('license_number')
        license_pdf = request.FILES.get('license_pdf')
        aadhaar_number = request.POST.get('aadhaar_number')
        aadhaar_pdf = request.FILES.get('aadhaar_pdf')
        location = request.POST.get('location')
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        special_request = request.POST.get('specialRequest')
        
        # Assuming your form has a field named 'car_listing'
        car_id = request.POST.get('car_id')
        owner_id = request.POST.get('owner_email')
        user_id = request.POST.get('user_email')
        # Create and save your model instance
        Booking.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile_number=mobile_number,
            license_number=license_number,
            license_pdf=license_pdf,
            aadhaar_number=aadhaar_number,
            aadhaar_pdf=aadhaar_pdf,
            location=location,
            start_date=start_date,
            end_date=end_date,
            special_request=special_request,
            car_listing_id=car_id,
            user_id=user_id,
            car_owner_id=owner_id,
            
              # Associate the booking with a specific car listing
        )

        return HttpResponse('Booking successful!')  # You can redirect or render another template

    return render(request, 'booking.html', {'car_listing': car_id, 'car_owner': owner, 'user': client})
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

@login_required

def index2(request):
    if 'email' in request.session or 'username' in request.session:
        # Retrieve all cars added by car owners
        all_cars = CarListing.objects.all()

        # Fetch images for each car
        for car in all_cars:
            car.images = CarImage.objects.filter(car=car)

        # Retrieve email from session
        user_email = request.session.get('email', None)

        context = {
            'all_cars': all_cars,
            'user_email': user_email,  # Add user_email to the context
        }

        response = render(request, 'index2.html', context)
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

from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def adminreg(request):
    if request.method == 'POST':
        # Handle user status update
        for user in Usertable.objects.exclude(is_superuser=True):
            status_field_name = f'user_status_{user.email}'
            user_status = request.POST.get(status_field_name, '')

            if user_status == 'on':
                if not user.is_active:
                    user.is_active = True
                    user.save()
                    send_activation_email(user)
                else:
                    continue
            else:
                if user.is_active:
                    user.is_active = False
                    user.save()
                    send_deactivation_email(user)
                else:
                    continue

        # Handle car owner proposal status update
        for carowner in CarOwner.objects.all():
            status_field_name = f'proposal_status_{carowner.email}'
            proposal_status = request.POST.get(status_field_name, 'Pending')

            if proposal_status == 'Accepted' and carowner.proposal_status != 'Accepted':
                # Generate random password for the car owner
                password = generate_random_password()
                # Set hashed password for the CarOwner
                carowner.password = make_password(password)
                carowner.save()

                # Send password and proposal notification email to car owner
                send_password_email(carowner, password)
                send_proposal_notification(carowner, proposal_status)
            elif proposal_status != 'Accepted':
                carowner.password_generated = False
                carowner.save()

            carowner.proposal_status = proposal_status
            carowner.save()

        # Handle driver registration
        if 'update_drivers_status' in request.POST:
            for driver in Driver.objects.all():
                status_field_name = f'driver_status_{driver.email}'
                driver_status = request.POST.get(status_field_name, '')

                if driver_status == 'on':
                    if not driver.status == 'Accepted':
                        driver.status = 'Accepted'
                        driver.save()
                        send_driver_password_email(driver)
                else:
                    if driver.status == 'Accepted':
                        driver.status = 'Rejected'
                        driver.save()

    admin_users = Usertable.objects.filter(role='admin')
    normal_users = Usertable.objects.filter(role='normal_user')
    club_users = Usertable.objects.filter(role='club_user')
    car_owners = CarOwner.objects.all()
    drivers = Driver.objects.all()

    context = {
        'admin_users': admin_users,
        'normal_users': normal_users,
        'club_users': club_users,
        'car_owners': car_owners,
        'drivers': drivers,
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
def driverreg(request):
    return render(request, "driverreg.html")

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

from django.shortcuts import render
from .models import CarOwner, CarListing

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required


# def index3(request):
#     # Retrieve the currently logged-in car owner 
    
 
#     return render(request, 'index3.html')

from django.shortcuts import render, redirect
from .models import CarListing, CarImage

def index3(request):
    if 'email' in request.session:
        # Retrieve the currently logged-in car owner
        car_owner = CarOwner.objects.get(email=request.session['email'])

        # Retrieve the cars added by the car owner
        user_cars = CarListing.objects.filter(car_owner=car_owner)

        # Fetch images for each car
        for car in user_cars:
            car.images = CarImage.objects.filter(car=car)

        context = {
            'user_cars': user_cars,
        }

        response = render(request, 'index3.html', context)
        response['Cache-Control'] = 'no-store, must-revalidate'
        return response
    else:
        return redirect('index')



from django.shortcuts import render, redirect
from .models import CarListing





def addcar(request):
    if request.method == 'POST':
        make = request.POST['make']
        model = request.POST['model']
        year = request.POST['year']
        description = request.POST['description']
        price = request.POST['price']

        # Handle multiple file uploads
        images = request.FILES.getlist('images')

        # Get the currently logged-in car owner
        car_owner = CarOwner.objects.get(email=request.session['email'])

        # Create a new car listing object and save it to the database
        car = CarListing(
            car_owner=car_owner,
            make=make,
            model=model,
            year=year,
            description=description,
            price=price
        )
        car.save()

        # Save images for the car
        for image in images:
            CarImage.objects.create(car=car, image=image)

        return redirect('index3')  # Redirect to a car listings page

    return render(request, 'addcar.html')
@login_required
def car_details(request, car_id, user_id):
    car = get_object_or_404(CarListing, pk=car_id)
    car_images = CarImage.objects.filter(car=car)
    context = {'car': car, 'car_images': car_images , 'user':user_id}
    return render(request, 'car_details.html', context)
from .models import CarAccessory, AccessoryImage
@login_required
def addtools(request):
    if request.method == 'POST':
        # Extract data from the form
        name = request.POST.get('name')
        accessory_id = request.POST.get('accessory_id')
        category = request.POST.get('category')
        price = request.POST.get('price')
        compatibility = request.POST.get('compatibility')
        quantity_available = request.POST.get('quantity_available')
        description = request.POST.get('description')
        installation_requirements = request.POST.get('installation_requirements')
        manufacturer = request.POST.get('manufacturer')
        material = request.POST.get('material')
        dimensions_weight = request.POST.get('dimensions_weight')
        thumbnail = request.FILES.get('thumbnail')
        images = request.FILES.getlist('images')

        # Create a CarAccessory instance
        accessory = CarAccessory.objects.create(
            name=name,
            accessory_id=accessory_id,
            category=category,
            price=price,
            compatibility=compatibility,
            quantity_available=quantity_available,
            description=description,
            installation_requirements=installation_requirements,
            manufacturer=manufacturer,
            material=material,
            dimensions_weight=dimensions_weight,
            thumbnail=thumbnail
        )

        # Create AccessoryImage instances for each image
        for image in images:
            AccessoryImage.objects.create(accessory=accessory, image=image)

        # Redirect to a success page or do something else
        return redirect('adminreg')  # Replace 'success' with the name of your success URL pattern

    return render(request, 'addtools.html')
from django.contrib.auth.decorators import login_required

@login_required
def shop(request, user_email):
    # Retrieve all car accessories from the database
    accessories = CarAccessory.objects.all()
    context = {'accessories': accessories, 'user_email': user_email}
    return render(request, 'shop.html', context)

@login_required
def accessory_details(request, accessory_id, user_email):
    # Retrieve the accessory object
    accessory = get_object_or_404(CarAccessory, pk=accessory_id)
    
    # Pass accessory and user_email to the template context
    context = {
        'accessory': accessory,
        'user_email': user_email,
    }
    return render(request, 'accessory_details.html', context)

# views.py

from django.shortcuts import render, redirect
from .models import Driver

def driverreg(request):
    if request.method == 'POST':
        driver_name = request.POST.get('driver_name')
        email = request.POST.get('email')
        contact_number = request.POST.get('contact_number')
        driver_license = request.FILES.get('driver_license')
        conduct_certificate = request.FILES.get('conduct_certificate')
        address = request.POST.get('address')
        location = request.POST.get('location')
        district = request.POST.get('district')
        photo = request.FILES.get('photo')

        driver = Driver.objects.create(
            driver_name=driver_name,
            email=email,
            contact_number=contact_number,
            driver_license=driver_license,
            conduct_certificate=conduct_certificate,
            address=address,
            location=location,
            district=district,
            photo=photo
        )
        return redirect('registration_success')  # Assuming you have a URL named 'registration_success'

    return render(request, 'driverreg.html')
# views.py

from django.shortcuts import render, redirect

def submit_registration(request):
    # Your code to handle form submission and insert data into the database
    return redirect('registration_success')  # Redirect to a success page after successful submission

# views.py

from django.http import HttpResponse

def registration_success(request):
    return HttpResponse("Registration successful. Thank you!")
    
def addtocart(request):
    return render(request, "addtocart.html")






# views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import CartItem

from django.shortcuts import redirect, get_object_or_404
from .models import CartItem, CarAccessory

def add_to_cart(request, accessory_id):
    # Get the accessory object using the accessory_id
    accessory = get_object_or_404(CarAccessory, pk=accessory_id)

    # Check if the user already has the item in the cart
    user_cart_item, created = CartItem.objects.get_or_create(user=request.user, product=accessory)

    if not created:
        # If the cart item already exists, check if its quantity is less than 4
        if user_cart_item.quantity < 4:
            # Increment the quantity by 1 if it's less than 4
            user_cart_item.quantity += 1
            user_cart_item.save()
        else:
            # If the quantity is already 4, show a message and do not update the quantity
            messages.warning(request, 'You can only add up to 4 quantities of this item.')

    return redirect('cart')


def remove_from_cart(request, item_id):
    # Retrieve the cart item
    cart_item = get_object_or_404(CartItem, pk=item_id)

    # Decrease the quantity by one
    cart_item.quantity -= 1

    # Save the cart item if quantity is greater than zero, otherwise delete it
    if cart_item.quantity > 0:
        cart_item.save()
    else:
        cart_item.delete()

    # Redirect back to the cart page
    return redirect('cart')

def view_cart(request):
    # Get cart items for the current user
    cart_items = CartItem.objects.filter(user=request.user)

    context = {
        'cart_items': cart_items,
    }

    return render(request, 'cart.html', context)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import CartItem
def update_cart(request, item_id, quantity):
    cart_item = get_object_or_404(CartItem, pk=item_id)
    cart_item.quantity = quantity
    cart_item.save()

    return JsonResponse({'quantity': cart_item.quantity, 'subtotal': cart_item.subtotal})

from django.shortcuts import render
from .models import Wishlist

def wishlist(request):
    # Retrieve the wishlist items for the current user
    user_email = request.user.email
    wishlist_items = Wishlist.objects.filter(user=request.user)

    # Pass wishlist items and user_email to the template context
    context = {
        'wishlist_items': wishlist_items,
        'user_email': user_email,
    }
    return render(request, 'wishlist.html', context)

from django.shortcuts import redirect, get_object_or_404
from .models import CarAccessory, Wishlist

from django.shortcuts import get_object_or_404

from django.shortcuts import get_object_or_404
@login_required
def add_to_wishlist(request, accessory_id):
    if request.method == 'POST':
        # Assuming you have a logged-in user
        user = request.user
        accessory = get_object_or_404(CarAccessory, id=accessory_id)
        
        # Get or create the user's wishlist
        wishlist, created = Wishlist.objects.get_or_create(user=user, product=accessory)
        
        return redirect('wishlist')  # Redirect to the wishlist page
    else:
        return redirect('cart')
    

   
from .models import Wishlist

def remove_from_wishlist(request, wishlist_id):
    if request.method == 'POST':
        wishlist_item = Wishlist.objects.get(id=wishlist_id)
        wishlist_item.delete()
        return redirect('wishlist')
    else:
        return redirect('wishlist')
    






from django.shortcuts import render, redirect
from .models import CartItem, Checkout

from django.shortcuts import render, redirect
from .models import CartItem, Checkout

def checkout(request):
    if request.method == 'POST':
        # Retrieve the user's cart items
        cart_items = CartItem.objects.filter(user=request.user)
        
        # Calculate total price
        total_price = sum(item.subtotal for item in cart_items)

        # Extract shipping information from the form
        full_name = request.POST.get('full_name')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2', '')  # Optional field
        city = request.POST.get('city')
        state = request.POST.get('state')
        pin_code = request.POST.get('pin_code')
        phone_number = request.POST.get('phone_number')

        # Save checkout information
        checkout = Checkout.objects.create(
            user=request.user,
            full_name=full_name,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            city=city,
            state=state,
            pin_code=pin_code,
            phone_number=phone_number
        )

        # You can associate each cart item with this checkout instance if needed
        for item in cart_items:
            item.checkout = checkout
            item.save()

        # Redirect to order confirmation page
        return redirect('order_confirmation')  # Redirect to the order confirmation page
    else:
        # If the request method is GET, retrieve cart items and calculate total price
        cart_items = CartItem.objects.filter(user=request.user)
        total_price = sum(item.subtotal for item in cart_items)

        # Pass cart items and total price to the template
        context = {
            'cart_items': cart_items,
            'total_price': total_price,
        }

        return render(request, 'checkout.html', context)

    

from django.shortcuts import render
from .models import Checkout

from django.shortcuts import render
from .models import Checkout

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Checkout

def order_confirmation(request):
    try:
        # Retrieve the latest checkout information for the user
        latest_checkout = Checkout.objects.filter(user=request.user).latest('created_at')
        
        # Retrieve checkout items associated with the latest checkout
        checkout_items = latest_checkout.items.all()

        # Calculate total price from checkout items
        total_price = sum(item.subtotal for item in checkout_items)

        context = {
            'checkout': latest_checkout,
            'checkout_items': checkout_items,
            'total_price': total_price,
        }
        return render(request, 'order_confirmation.html', context)
    except Checkout.DoesNotExist:
        messages.error(request, "No checkout information found. Please complete the checkout process first.")
        return redirect('cart')  # Redirect to the cart page





