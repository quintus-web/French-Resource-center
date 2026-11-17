from django.contrib import admin
from django.utils.html import format_html
from .models import Author, Publisher, Subject, Series, Resource, BookCopy, DigitalMaterial


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'nationality', 'resource_count')
    search_fields = ('last_name', 'first_name', 'nationality')
    ordering = ('last_name', 'first_name')

    @admin.display(description='# Resources')
    def resource_count(self, obj):
        return obj.resources.count()


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'website', 'resource_count')
    search_fields = ('name', 'country')

    @admin.display(description='# Resources')
    def resource_count(self, obj):
        return obj.resources.count()


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'resource_count')
    search_fields = ('name',)

    @admin.display(description='# Resources')
    def resource_count(self, obj):
        return obj.resources.count()


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'resource_count')
    search_fields = ('name',)

    @admin.display(description='# Resources')
    def resource_count(self, obj):
        return obj.resources.count()


class BookCopyInline(admin.TabularInline):
    model = BookCopy
    extra = 1
    fields = ('accession_number', 'shelf_location', 'condition', 'status', 'acquisition_source', 'acquired_date', 'notes')
    show_change_link = True


class DigitalMaterialInline(admin.TabularInline):
    model = DigitalMaterial
    extra = 0
    fields = ('title', 'file', 'external_url')


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = (
        'cover_thumbnail', 'title', 'author_display', 'publisher',
        'call_number', 'level', 'category', 'language',
        'available_copies_display', 'total_copies_display',
    )
    list_display_links = ('title',)
    list_filter = ('level', 'category', 'language', 'series', 'subjects', 'publisher')
    search_fields = ('title', 'subtitle', 'authors__last_name', 'isbn', 'call_number', 'copies__accession_number')
    filter_horizontal = ('authors', 'subjects')
    autocomplete_fields = ('publisher', 'series')
    inlines = [BookCopyInline, DigitalMaterialInline]
    list_per_page = 25
    fieldsets = (
        ('Bibliographic Details', {
            'fields': (
                'title', 'subtitle', 'authors', 'publisher',
                'publication_year', 'edition', 'isbn',
            )
        }),
        ('Classification', {
            'fields': (
                'call_number', 'level', 'category', 'subjects',
                'series', 'series_number', 'language',
            )
        }),
        ('Description & Media', {
            'fields': ('description', 'cover_image'),
        }),
    )

    @admin.display(description='Cover')
    def cover_thumbnail(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="height:40px;border-radius:3px;">', obj.cover_image.url)
        return '—'

    @admin.display(description='Authors')
    def author_display(self, obj):
        return obj.author_display

    @admin.display(description='Available')
    def available_copies_display(self, obj):
        return obj.available_copies_count

    @admin.display(description='Total Copies')
    def total_copies_display(self, obj):
        return obj.total_copies_count


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = (
        'accession_number', 'resource_title', 'level_badge',
        'condition', 'status', 'shelf_location',
        'acquisition_source', 'acquired_date', 'donor_name',
    )
    list_filter = ('status', 'condition', 'acquisition_source', 'resource__level', 'resource__category')
    search_fields = ('accession_number', 'resource__title', 'shelf_location', 'donor_name')
    list_editable = ('status', 'condition', 'shelf_location')
    list_per_page = 30
    fieldsets = (
        ('Copy Details', {
            'fields': ('resource', 'accession_number', 'shelf_location', 'condition', 'status', 'notes')
        }),
        ('Acquisition', {
            'fields': ('acquisition_source', 'acquisition_cost', 'acquired_date', 'donor_name')
        }),
    )

    @admin.display(description='Title', ordering='resource__title')
    def resource_title(self, obj):
        return obj.resource.title

    @admin.display(description='CEFR Level')
    def level_badge(self, obj):
        return obj.resource.level


@admin.register(DigitalMaterial)
class DigitalMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource', 'uploaded_at', 'has_file', 'has_url')
    search_fields = ('title', 'resource__title')
    list_filter = ('uploaded_at',)

    @admin.display(boolean=True, description='File')
    def has_file(self, obj):
        return bool(obj.file)

    @admin.display(boolean=True, description='URL')
    def has_url(self, obj):
        return bool(obj.external_url)
