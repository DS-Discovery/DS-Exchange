from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import Application


@receiver(post_save, sender=Application)
def my_callback(sender, **kwargs):
    if kwargs["created"]:
        html_message = render_to_string("emails/app_confirmation.html", {"project": kwargs["instance"].project})
        plain_message = strip_tags(html_message)

        send_mail(
            "DS Discovery Application Confirmation",
            plain_message,
            settings.EMAIL_HOST_USER,
            [kwargs["instance"].student.email_address],
            html_message=html_message,
        )

        print(f"Sent confirmation email to {kwargs['instance'].student.email_address}")
