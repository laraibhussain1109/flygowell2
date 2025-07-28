from django.core.mail import send_mail
import random

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    subject = "Your FlyGoWell Email Verification OTP"
    message = f"Welcome to FlyGoWell!\nYour OTP is: {otp}"
    from_email = "your_email@gmail.com"
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
