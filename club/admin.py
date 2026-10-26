from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Attendance, ClubEvent, DELFStudyResource


class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    autocomplete_fields = ['member']
    fields = ('member', 'present', 'remarks')


@admin.register(ClubEvent)
class ClubEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'date', 'location', 'attendee_count_display', 'is_completed')
    list_filter = ('event_type', 'is_completed', 'date')
    search_fields = ('title', 'location', 'description')
    inlines = [AttendanceInline]

    @admin.display(description='Attendees')
    def attendee_count_display(self, obj):
        return obj.attendee_count


@admin.register(DELFStudyResource)
class DELFStudyResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'skill', 'is_pinned', 'created_at')
    list_filter = ('level', 'skill', 'is_pinned')
    search_fields = ('title', 'description', 'url')
    list_editable = ('is_pinned',)