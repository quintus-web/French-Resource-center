# Register your models here.
from django.contrib import admin
from .models import Resource, BookCopy, DigitalMaterial


class BookCopyInline(admin.TabularInline):
    model = BookCopy
    extra = 1
    fields = ('accession_number', 'shelf_location', 'condition', 'status', 'notes')
    show_change_link = True


class DigitalMaterialInline(admin.TabularInline):
    model = DigitalMaterial
    extra = 0
    fields = ('title', 'file', 'external_url')


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'author', 
        'level', 
        'category', 
        'available_copies_display', 
        'total_copies_display',
        'created_at'
    )
    list_filter = ('level', 'category', 'created_at')
    search_fields = ('title', 'author', 'isbn', 'copies__accession_number')
    inlines = [BookCopyInline, DigitalMaterialInline]
    list_per_page = 25

    @admin.display(description='Available')
    def available_copies_display(self, obj):
        return obj.available_copies_count

    @admin.display(description='Total Copies')
    def total_copies_display(self, obj):
        return obj.total_copies_count


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ('accession_number', 'resource_title', 'level_badge', 'condition', 'status', 'shelf_location')
    list_filter = ('status', 'condition', 'resource__level', 'resource__category')
    search_fields = ('accession_number', 'resource__title', 'shelf_location')
    list_editable = ('status', 'condition')
    list_per_page = 30

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