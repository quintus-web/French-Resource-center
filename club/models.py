from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from lending.models import Borrower


class ClubEvent(models.Model):
    EVENT_TYPES = [
        ('MEETING', 'Réunion hebdomadaire (Weekly Meeting)'),
        ('MOVIE', 'Soirée Cinéma (French Movie Screening)'),
        ('DEBATE', 'Débat francophone (Debate Competition)'),
        ('WORKSHOP', 'Atelier pratique (Pronunciation & Culture)'),
        ('DELF_PREP', 'Préparation DELF / DALF Workshop'),
    ]

    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='MEETING')
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=150, default='French Resource Center', help_text='Room or venue')
    description = models.TextField(blank=True, help_text='Agenda or topics to be covered')
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-start_time']
        verbose_name = 'Club Event'
        verbose_name_plural = 'Club Events'

    def __str__(self):
        return f"{self.title} ({self.date.strftime('%d %b %Y')})"

    @property
    def attendee_count(self):
        return self.attendances.filter(present=True).count()


class Attendance(models.Model):
    event = models.ForeignKey(ClubEvent, on_delete=models.CASCADE, related_name='attendances')
    member = models.ForeignKey(Borrower, on_delete=models.CASCADE, related_name='event_attendances')
    present = models.BooleanField(default=True)
    remarks = models.CharField(max_length=200, blank=True, help_text='Optional remarks (e.g., debate speaker, late)')

    class Meta:
        unique_together = ('event', 'member')
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        status = "Present" if self.present else "Absent"
        return f"{self.member} - {self.event.title} [{status}]"


class DELFStudyResource(models.Model):
    LEVEL_CHOICES = [
        ('A1', 'DELF Prim / Junior A1'),
        ('A2', 'DELF Junior A2'),
        ('B1', 'DELF Scolaire / Junior B1'),
        ('B2', 'DELF B2'),
    ]

    SKILL_CHOICES = [
        ('CO', 'Compréhension de l’oral (Listening)'),
        ('CE', 'Compréhension des écrits (Reading)'),
        ('PE', 'Production écrite (Writing)'),
        ('PO', 'Production orale (Speaking)'),
        ('GRAMMAR', 'Grammaire & Conjugaison'),
    ]

    title = models.CharField(max_length=255)
    level = models.CharField(max_length=5, choices=LEVEL_CHOICES, db_index=True)
    skill = models.CharField(max_length=10, choices=SKILL_CHOICES, default='CO')
    url = models.URLField(help_text='Direct link to podcast, TV5Monde, RFI Savoirs, or France Education drive')
    description = models.CharField(max_length=255, blank=True, help_text='Brief instruction for students')
    is_pinned = models.BooleanField(default=False, help_text='Pin to top of study dashboard')
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', 'level', 'skill']
        verbose_name = 'DELF Study Link'
        verbose_name_plural = 'DELF Study Links'

    def __str__(self):
        return f"[{self.level} - {self.skill}] {self.title}"


class EventPhoto(models.Model):
    event = models.ForeignKey(ClubEvent, on_delete=models.CASCADE, related_name='photos', null=True, blank=True)
    caption = models.CharField(max_length=200, help_text="e.g. Concours d'Éloquence winners 2026")
    image = models.ImageField(upload_to='events/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.caption


class ClubDocument(models.Model):
    DOC_TYPES = [
        ('DELF', 'Past DELF Exam Papers'),
        ('SYLLABUS', 'Curriculum & Syllabi'),
        ('GAZETTE', 'Club Journal / Newsletter'),
        ('MINUTES', 'Meeting Minutes & Constitution'),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=DOC_TYPES, default='DELF')
    description = models.CharField(max_length=255, blank=True)
    file = models.FileField(
        upload_to='documents/%Y/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'epub', 'xlsx'])]
    )
    uploaded_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"


class PodcastEpisode(models.Model):
    title = models.CharField(max_length=200)
    episode_number = models.PositiveIntegerField(default=1)
    description = models.TextField(help_text="Vocabulary breakdown, host notes, or transcript excerpts")
    audio_file = models.FileField(
        upload_to='podcasts/%Y/',
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'm4a', 'aac'])],
        blank=True,
        null=True,
        help_text="Upload raw audio file (.mp3)"
    )
    external_url = models.URLField(
        blank=True,
        help_text="Optional Spotify, YouTube, or Apple Podcasts link"
    )
    duration_minutes = models.PositiveIntegerField(default=10, help_text="Estimated duration in minutes")
    published_date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-published_date', '-episode_number']

    def __str__(self):
        return f"Ep. {self.episode_number}: {self.title}"