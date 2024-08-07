import six

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import get_template

from rest_framework_simplejwt.tokens import RefreshToken


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):

        return (six.text_type(user.pk)+six.text_type(timestamp) + six.text_type(user.is_verified))
    
def send_mail(file_name, reciever_email, data=None):
    html_tpl_path = f"email-templates/{file_name}.html"
    email_html_template = get_template(html_tpl_path).render(data)
    email_msg = EmailMessage(
        "Proace International",
        email_html_template,
        settings.APPLICATION_EMAIL,
        [reciever_email],
        reply_to=[settings.APPLICATION_EMAIL],
    )
    email_msg.content_subtype = "html"
    email_msg.send(fail_silently=False)
    
def auth_token(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }