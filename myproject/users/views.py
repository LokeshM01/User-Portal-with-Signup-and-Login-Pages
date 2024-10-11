from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .forms import CustomerForm
from django.contrib.auth.decorators import login_required
from .models import Customer
import requests
from django.utils.timezone import now  # To calculate age
import urllib.parse  # For encoding the WhatsApp message
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import AdminActivityLog
from django.utils.timezone import now
import json
from django.http import JsonResponse
from django.conf import settings
from django.core.mail import send_mail
import os
from .utils import generate_customer_pdf 

WEBHOOK_URL = 'http://127.0.0.1:8000/webhook-receiver/'


@login_required
def dashboard_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            # Save the customer details to the database
            customer = form.save()

            # Generate the PDF with customer details
            pdf_path = generate_customer_pdf(customer)

            if pdf_path:
                # Store the PDF path in the database
                customer.pdf_file_path = pdf_path
                customer.save()
            else:
                print("PDF generation failed") 

            # Combine country code and phone number (remove any non-numeric characters like '+')
            country_code = customer.country_code.strip('+').replace(' ', '')  # Strip '+' and any spaces from the country code
            full_phone_number = f"{country_code}{customer.phone_number.replace(' ', '').replace('-', '')}"  # Strip spaces and dashes from the phone number

            # Calculate age from birthdate (if provided)
            if customer.birthdate:
                current_year = now().year
                birth_year = customer.birthdate.year
                age = current_year - birth_year
            else:
                age = "N/A"

            # Log the form submission as an admin activity
            AdminActivityLog.objects.create(
                user=request.user,
                action="Customer form submitted",
                details=f"Customer name: {customer.name}, Email: {customer.email}, Phone: {full_phone_number}",
                timestamp=now()
            )

            # Prepare WhatsApp message
            whatsapp_message = (
                f"Hello Mr {customer.name},\n\n"
                f"This message is to inform you that you have been successfully added as a customer at Inditech.  \n"
                f"Please verify your details:  \n"
                f"Name: {customer.name }  \n"
                f"Age: {age  }  \n"
                f"Email: {customer.email }\n"
                f"Phone: {full_phone_number }\n"
                "If the details are correct, please reply 'CORRECT'. If any changes are needed, reply 'To be Changed'. \n"
                "Please reply within 48 hours or we will assume your reply as 'CORRECT'. \n\n"
                "Thanks and regards, \n"
                "Team Inditech "
            )

            # URL-encode the WhatsApp message
            encoded_message = urllib.parse.quote(whatsapp_message)

            # Pass the WhatsApp URL with the encoded message
            whatsapp_url = f"https://api.whatsapp.com/send?phone={full_phone_number}&text={encoded_message}"

            print(f"WhatsApp URL: {whatsapp_url}")
            # Redirect to the thank you page with the WhatsApp URL in the query string
            encoded_whatsapp_url = urllib.parse.quote_plus(whatsapp_url)
            return HttpResponseRedirect(f"/users/thank_you/?whatsapp_url={encoded_whatsapp_url}")

    else:
        form = CustomerForm()

    return render(request, 'dashboard.html', {'form': form})



@login_required
def thank_you_view(request):
    # Retrieve the WhatsApp URL from the query string
    # whatsapp_url = request.GET.get('whatsapp_url', '')

    encoded_whatsapp_url = request.GET.get('whatsapp_url', '')
    whatsapp_url = urllib.parse.unquote_plus(encoded_whatsapp_url)

    print(f"WhatsApp URL2: {whatsapp_url}")
    # Pass the WhatsApp URL to the template for rendering
    return render(request, 'thank_you.html', {'whatsapp_url': whatsapp_url})

# List all customers with pagination
def customer_list_view(request):
    customers = Customer.objects.all()
    paginator = Paginator(customers, 100)  # Show 10 customers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Log that admin viewed the customer list
    AdminActivityLog.objects.create(
        user=request.user,
        action="Viewed customer list",
        details=f"Page {page_number}",
        timestamp=now()
    )
    return render(request, 'customer_list.html', {'page_obj': page_obj})

# View a single customer's details
def customer_detail_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    # Log that admin viewed a customer's details
    AdminActivityLog.objects.create(
        user=request.user,
        action="Viewed customer details",
        details=f"Customer ID: {customer.id}, Name: {customer.name}",
        timestamp=now()
    )

    return render(request, 'customer_detail.html', {'customer': customer})

# Edit a customer's details

def customer_edit_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()

            # Log the customer edit action
            AdminActivityLog.objects.create(
                user=request.user,
                action="Edited customer details",
                details=f"Customer ID: {customer.id}, Name: {customer.name}",
                timestamp=now()
            )

            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'customer_form.html', {'form': form})


# Delete a customer
def customer_delete_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        customer.delete()

        # Log the customer delete action
        AdminActivityLog.objects.create(
            user=request.user,
            action="Deleted customer",
            details=f"Customer ID: {customer.id}, Name: {customer.name}",
            timestamp=now()
        )

        return redirect('customer_list')

    return render(request, 'customer_confirm_delete.html', {'customer': customer})

def webhook_receiver(request):
    if request.method == 'POST':  # Only allow POST requests for webhooks
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)

            # Verify that the webhook secret matches the one in settings
            if data.get('secret') != settings.WEBHOOK_SECRET:
                return JsonResponse({'error': 'Unauthorized request'}, status=401)

            # Process the webhook data (e.g., notify admins, update records)
            print(f"Webhook received: {data}")

            # You can log the webhook event, notify admins, or trigger further actions
            return JsonResponse({'status': 'Webhook received and processed'}, status=200)

        except json.JSONDecodeError:  # Catch JSON decoding errors
            return JsonResponse({'error': 'Invalid payload'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def notify_admins(customer):
    subject = 'New Customer Form Submitted'
    message = f"Customer {customer.name} has submitted a form."
    admin_email = 'admin@example.com'  # Replace with the actual admin email

    send_mail(
        subject,
        message,
        'noreply@yourdomain.com',  # Replace with your own sender email
        [admin_email],
    )

def test_webhook_trigger(request):
    # Prepare sample data for the webhook
    webhook_data = {
        'user': 'testuser',  # Simulated user data
        'action': 'Test webhook trigger',
        'details': {
            'name': 'Test Name',
            'email': 'test@example.com',
            'phone_number': '+1234567890',
            'submitted_at': '2024-10-11 12:00:00'  # Example timestamp
        },
        'secret': settings.WEBHOOK_SECRET  # Include the secret to validate the webhook
    }

    # Trigger the webhook by sending a POST request
    try:
        response = requests.post(WEBHOOK_URL, json=webhook_data)
        response.raise_for_status()  # Raise an error if the request fails
        return JsonResponse({'status': 'Webhook triggered successfully'}, status=200)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Failed to trigger webhook: {e}'}, status=500)
