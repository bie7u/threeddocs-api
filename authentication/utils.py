from django.utils.html import strip_tags
from rest_framework import serializers
from threeddocs import settings
from django.core.mail import EmailMultiAlternatives


def send_password_reset_email(email, uuid):
    try:
        subject = 'Reset Your Password'
        link = f"{settings.FRONTEND_HOST}/reset-password?token={uuid}"
        html_content =f"""
    <div style="font-family: Arial, sans-serif; color: #333;">
        <h2>Witaj!</h2>
        <p>Otrzymaliśmy prośbę o zresetowanie hasła do Twojego konta w serwisie <b>Threeddocsy</b>.</p>
        <p>Kliknij w poniższy przycisk, aby ustawić nowe hasło:</p>
        <div style="margin: 20px 0;">
            <a href="{link}" 
               style="background-color: #2c3e50; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
               Zmień hasło
            </a>
        </div>
        <p style="font-size: 12px; color: #777;">
            Jeśli przycisk nie działa, skopiuj ten link: <br>
            {link}
        </p>
    </div>
    """
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception as e:
        raise serializers.ValidationError(str(e))
