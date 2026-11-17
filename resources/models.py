from django.db import models
from django.core.validators import FileExtensionValidator


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Publisher(models.Model):
    name = models.CharField(max_length=255, unique=True)
    country = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Publisher'
        verbose_name_plural = 'Publishers'

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'

    def __str__(self):
        return self.name


class Series(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Series / Collection'
        verbose_name_plural = 'Series / Collections'

    def __str__(self):
        return self.name


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

    LANGUAGE_CHOICES = [
        ('FR', 'French'),
        ('FR_EN', 'French / English Bilingual'),
        ('EN', 'English (about French)'),
        ('OTHER', 'Other'),
    ]

    # Core bibliographic fields
    title = models.CharField(max_length=255, db_index=True)
    subtitle = models.CharField(max_length=255, blank=True)
    authors = models.ManyToManyField(Author, related_name='resources', blank=True)
    publisher = models.ForeignKey(
        Publisher, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='resources'
    )
    publication_year = models.PositiveIntegerField(null=True, blank=True)
    edition = models.CharField(max_length=50, blank=True, help_text="e.g. 2nd Edition, Revised")
    isbn = models.CharField(max_length=30, blank=True, db_index=True, help_text="ISBN-10 or ISBN-13")

    # Classification
    call_number = models.CharField(
        max_length=30, blank=True, db_index=True,
        help_text="Dewey Decimal or local call number (e.g. 448.2 DUM)"
    )
    level = models.CharField(max_length=5, choices=LEVEL_CHOICES, default='GEN', db_index=True)
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='NOVEL', db_index=True)
    subjects = models.ManyToManyField(Subject, related_name='resources', blank=True)
    series = models.ForeignKey(
        Series, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='resources'
    )
    series_number = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Volume/part number within the series"
    )
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='FR')

    # Description & media
    description = models.TextField(blank=True, help_text="Brief synopsis or syllabus relevance")
    cover_image = models.ImageField(
        upload_to='covers/%Y/', blank=True, null=True,
        help_text="Front cover thumbnail"
    )

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

    @property
    def author_display(self):
        return ', '.join(a.full_name for a in self.authors.all()) or '—'


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

    ACQUISITION_CHOICES = [
        ('PURCHASED', 'Purchased'),
        ('DONATED', 'Donated'),
        ('GRANT', 'Grant / Aid'),
        ('TRANSFER', 'Transfer from Another Library'),
        ('OTHER', 'Other'),
    ]

    resource = models.ForeignKey(Resource, related_name='copies', on_delete=models.CASCADE)
    accession_number = models.CharField(
        max_length=50, unique=True, db_index=True,
        help_text="Unique inventory shelf sticker ID (e.g. FR-BK-001)"
    )
    shelf_location = models.CharField(
        max_length=60, blank=True,
        help_text="Shelf/Row reference (e.g. Shelf B-2, Niveau A2)"
    )
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='GOOD')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='AVAILABLE', db_index=True)
    notes = models.CharField(max_length=255, blank=True, help_text="E.g., missing dust jacket, accompanied by CD")

    # Acquisition tracking
    acquisition_source = models.CharField(
        max_length=15, choices=ACQUISITION_CHOICES, default='PURCHASED', blank=True
    )
    acquisition_cost = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Purchase price in local currency"
    )
    acquired_date = models.DateField(null=True, blank=True, help_text="Date this copy was added to the collection")
    donor_name = models.CharField(max_length=255, blank=True, help_text="Name of donor if applicable")

    added_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['accession_number']
        verbose_name = 'Physical Copy'
        verbose_name_plural = 'Physical Copies'

    def __str__(self):
        return f"[{self.accession_number}] {self.resource.title} ({self.get_status_display()})"


class DigitalMaterial(models.Model):
    resource = models.ForeignKey(
        Resource, related_name='digital_files',
        on_delete=models.CASCADE, null=True, blank=True,
        help_text="Link to an existing catalog entry, or leave empty for standalone digital content"
    )
    title = models.CharField(max_length=255)
    file = models.FileField(
        upload_to='french_materials/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'mp3', 'docx', 'epub', 'zip'])],
        blank=True, null=True
    )
    external_url = models.URLField(
        blank=True,
        help_text="Direct link to external audio, YouTube video, or TV5Monde exercise"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
