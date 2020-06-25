from django.core.mail import send_mail


def get_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def send_notification(block_request):
    accepted = 'accepted' if block_request.is_accepted else 'not accepted'
    send_mail(
        subject=f'Your request about blocking {block_request.website.domain} was resolved',
        message=f'Your request from {block_request.created} about blocking {block_request.website.domain} has status '
        f'now {accepted}',
        from_email='admin444@gmail.com',
        recipient_list=[block_request.email],
    )
