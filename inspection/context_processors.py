from .models import InspectionSchedule
from django.utils.timezone import now

def active_schedule(request):
    if not request.user.is_authenticated:
        return {'active_schedule': None}

    current_time = now()
    schedule = InspectionSchedule.objects.filter(
        start_time__lte=current_time,
        end_time__gte=current_time
    ).first()
    return {'active_schedule': schedule}