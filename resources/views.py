from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from .models import Resource, BookCopy


def catalogue(request):
    qs = Resource.objects.select_related('publisher').prefetch_related('authors', 'copies')

    q = request.GET.get('q', '').strip()
    level = request.GET.get('level', '')
    category = request.GET.get('category', '')

    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(authors__first_name__icontains=q) |
            Q(authors__last_name__icontains=q) |
            Q(publisher__name__icontains=q) |
            Q(copies__accession_number__icontains=q)
        ).distinct()
    if level:
        qs = qs.filter(level=level)
    if category:
        qs = qs.filter(category=category)

    context = {
        'resources': qs,
        'level_choices': Resource.LEVEL_CHOICES,
        'category_choices': Resource.CATEGORY_CHOICES,
        'q': q,
        'selected_level': level,
        'selected_category': category,
        'total': qs.count(),
    }
    return render(request, 'resources/catalogue.html', context)


def resource_detail(request, pk):
    resource = get_object_or_404(
        Resource.objects.prefetch_related('copies', 'digital_files'),
        pk=pk
    )
    context = {
        'resource': resource,
        'available_copies': resource.copies.filter(status='AVAILABLE'),
        'other_copies': resource.copies.exclude(status='AVAILABLE'),
    }
    return render(request, 'resources/resource_detail.html', context)
