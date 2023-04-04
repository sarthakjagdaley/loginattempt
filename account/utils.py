from django.core.mail import EmailMessage
from django.conf import settings

import os

class Util:
    @staticmethod
    def send_email(data):
        
        email = EmailMessage(
            subject = data['subject'],
            body = data['body'],
            # from_email = settings.EMAIL_HOST_USER,
            from_email = os.getenv('EMAIL_FROM'),
            to=[data['to_email']]
        )
    
        email.send()
        