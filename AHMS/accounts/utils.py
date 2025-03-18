from django.core.mail import send_mail
from django.conf import settings


def email():
    subject="Test email for django project"
    message="Test email for django project"
    from_email = f'MediCare <{settings.EMAIL_HOST_USER}>'
    recipient_list=["aj123josh@gmail.com"]
    send_mail(subject,message,from_email,recipient_list)