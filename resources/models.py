# Create your models here.
from django.db import models
from django.core.validators import FileExtensionValidator


class Resource(models.Model):
    LEVEL_CHOICES = [
        ('A1', 'A1 - Débutant'),
        ('A2', 'A2 - Élémentaire'),
        ('B1', 'B1 - Intermédiaire'),
        ('B2', 'B2 - Avancé'),
        ('C1', 'C1 - Autonome'),
        ('GEN', 'Général / Reference'),
    ]

    CATEGORY_CHOICES = [
        ('NOVEL', 'Roman / Fiction'),
        ('GRAMMAR', 'Grammaire & Vocabulaire'),
        ('DELF', 'Préparation DELF / DALF'),
        ('COMIC', 'Bande Dessinée (BD)'),
        ('MAGAZINE', 'Revue / Journal'),
        ('DICTIONARY', 'Dictionnaire'),
        ('AUDIO_CD', 'CD Audio / Média'),
    ]

    title = models.CharField(max_length=255, db_index=True)
    author = models.CharField(max_length=255, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    publication_year = models.PositiveIntegerField(null=True, blank=True)
    isbn = models.CharField(max_length=30, blank=True, help_text="Optional ISBN or barcode number")
    level = models.CharField(max_length=5, choices=LEVEL_CHOICES, default='GEN', db_index=True)
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='NOVEL', db_index=True)
    description = models.TextField(blank=True, help_text="Brief synopsis or syllabus relevance")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'French Resource'
        verbose_name_plural = 'French Resources'

    def __str__(self):
        return f"{self.title} ({self.get_level_display()})"

    @property
    def total_copies_count(self):
        return self.copies.count()

    @property
    def available_copies_count(self):
        return self.copies.filter(status='AVAILABLE').count()


class BookCopy(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('ISSUED', 'Issued / On Loan'),
        ('RESERVED', 'Reserved'),
        ('MAINTENANCE', 'In Repair / Bindery'),
        ('LOST', 'Lost / Written Off'),
    ]

    CONDITION_CHOICES = [
        ('NEW', 'New / Excellent'),
        ('GOOD', 'Good'),
        ('WORN', 'Worn / Shelf Wear'),
        ('DAMAGED', 'Damaged / Needs Attention'),
    ]

    resource = models.ForeignKey(Resource, related_name='copies', on_delete=models.CASCADE)
    accession_number = models.CharField(
        max_length=50, 
        unique=True, 
        db_index=True, 
        help_text="Unique inventory shelf sticker ID (e.g. FR-BK-001)"
    )
    shelf_location = models.CharField(
        max_length=60, 
        blank=True, 
        help_text="Shelf/Row reference (e.g. Shelf B-2, Niveau A2)"
    )
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='GOOD')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='AVAILABLE', db_index=True)
    notes = models.CharField(max_length=255, blank=True, help_text="E.g., missing dust jacket, accompanied by CD")
    added_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['accession_number']
        verbose_name = 'Physical Copy'
        verbose_name_plural = 'Physical Copies'

    def __str__(self):
        return f"[{self.accession_number}] {self.resource.title} ({self.get_status_display()})"


class DigitalMaterial(models.Model):
    resource = models.ForeignKey(
        Resource, 
        related_name='digital_files', 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Link to an existing catalog entry, or leave empty for standalone digital content"
    )
    title = models.CharField(max_length=255)
    file = models.FileField(
        upload_to='french_materials/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'mp3', 'docx', 'epub', 'zip'])],
        blank=True,
        null=True
    )
    external_url = models.URLField(
        blank=True, 
        help_text="Direct link to external audio, YouTube video, or TV5Monde exercise"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title