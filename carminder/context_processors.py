from django.conf import settings


def company_name(request):
    return {"COMPANY_NAME": settings.COMPANY_NAME}
