from django.contrib import admin
from django.utils.html import format_html
from .models import ClubEvent, Attendance, DELFStudyResource, EventPhoto, ClubDocument, PodcastEpisode


class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    autocomplete_fields = ['member']
    fields = ('member', 'present', 'remarks')


class EventPhotoInline(admin.TabularInline):
    model = EventPhoto
    extra = 1
    fields = ('image', 'caption')


@admin.register(ClubEvent)
class ClubEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'date', 'location', 'attendee_count_display', 'is_completed')
    list_filter = ('event_type', 'is_completed', 'date')
    search_fields = ('title', 'location', 'description')
    inlines = [AttendanceInline, EventPhotoInline]

    @admin.display(description='Attendees')
    def attendee_count_display(self, obj):
        return obj.attendee_count


@admin.register(EventPhoto)
class EventPhotoAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'caption', 'event', 'uploaded_at')
    list_filter = ('event', 'uploaded_at')

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 35px; object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "-"
    thumbnail.short_description = 'Preview'


@admin.register(DELFStudyResource)
class DELFStudyResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'skill', 'is_pinned', 'created_at')
    list_filter = ('level', 'skill', 'is_pinned')
    search_fields = ('title', 'description', 'url')
    list_editable = ('is_pinned',)


@admin.register(ClubDocument)
class ClubDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_at', 'download_link')
    list_filter = ('category', 'uploaded_at')
    search_fields = ('title', 'description')

    def download_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank" style="padding: 2px 6px; background: #e0e7ff; color: #3730a3; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 11px;">View / Download</a>', obj.file.url)
        return "-"
    download_link.short_description = 'File'


@admin.register(PodcastEpisode)
class PodcastEpisodeAdmin(admin.ModelAdmin):
    list_display = ('episode_number', 'title', 'published_date', 'duration_minutes', 'has_audio')
    list_filter = ('published_date',)
    search_fields = ('title', 'description')

    @admin.display(boolean=True, description='Audio Attached')
    def has_audio(self, obj):
        return bool(obj.audio_file or obj.external_url)