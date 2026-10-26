from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from lending.models import Borrower
from .forms import ClubEventForm, DELFResourceForm
from .models import Attendance, ClubEvent, DELFStudyResource


@login_required
def club_dashboard(request):
    events = ClubEvent.objects.all()[:10]
    study_links = DELFStudyResource.objects.all()
    event_form = ClubEventForm()
    resource_form = DELFResourceForm()

    context = {
        'events': events,
        'study_links': study_links,
        'total_events': ClubEvent.objects.count(),
        'total_links': study_links.count(),
        'event_form': event_form,
        'resource_form': resource_form,
    }
    return render(request, 'club/dashboard.html', context)


@login_required
def create_event(request):
    if request.method == 'POST':
        form = ClubEventForm(request.POST)
        if form.is_valid():
            event = form.save()
            messages.success(request, f"Événement '{event.title}' scheduled successfully.")
    return redirect('club:dashboard')


@login_required
def event_attendance(request, event_id):
    event = get_object_or_404(ClubEvent, id=event_id)
    all_members = Borrower.objects.filter(is_active=True).order_by('last_name')
    existing_attendance = {att.member_id: att for att in event.attendances.select_related('member')}

    if request.method == 'POST':
        present_member_ids = request.POST.getlist('present_members')
        present_member_ids = [int(mid) for mid in present_member_ids]

        for member in all_members:
            is_present = member.id in present_member_ids
            Attendance.objects.update_or_create(
                event=event,
                member=member,
                defaults={'present': is_present}
            )

        event.is_completed = True
        event.save(update_fields=['is_completed'])
        messages.success(request, f"Attendance roll call updated for '{event.title}'.")
        return redirect('club:event_attendance', event_id=event.id)

    # Build attendance status list
    member_rows = []
    for member in all_members:
        att = existing_attendance.get(member.id)
        member_rows.append({
            'member': member,
            'is_present': att.present if att else False,
            'remarks': att.remarks if att else '',
        })

    context = {
        'event': event,
        'member_rows': member_rows,
        'present_count': sum(1 for r in member_rows if r['is_present']),
        'total_members': len(member_rows),
    }
    return render(request, 'club/attendance.html', context)


@login_required
def add_delf_resource(request):
    if request.method == 'POST':
        form = DELFResourceForm(request.POST)
        if form.is_valid():
            res = form.save()
            messages.success(request, f"DELF link '{res.title}' added to study center.")
    return redirect('club:dashboard')