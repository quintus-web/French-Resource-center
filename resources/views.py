from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from .models import Resource, Subject, Series


def catalogue(request):
    qs = Resource.objects.prefetch_related('authors', 'subjects').select_related('publisher', 'series')

    q = request.GET.get('q', '').strip()
    level = request.GET.get('level', '')
    category = request.GET.get('category', '')
    subject_id = request.GET.get('subject', '')
    series_id = request.GET.get('series', '')

    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(subtitle__icontains=q) |
            Q(authors__last_name__icontains=q) |
            Q(authors__first_name__icontains=q) |
            Q(isbn__icontains=q) |
            Q(call_number__icontains=q)
        ).distinct()
    if level:
        qs = qs.filter(level=level)
    if category:
        qs = qs.filter(category=category)
    if subject_id:
        qs = qs.filter(subjects__id=subject_id)
    if series_id:
        qs = qs.filter(series__id=series_id)

    context = {
        'resources': qs,
        'subjects': Subject.objects.all(),
        'series_list': Series.objects.all(),
        'level_choices': Resource.LEVEL_CHOICES,
        'category_choices': Resource.CATEGORY_CHOICES,
        'q': q,
        'selected_level': level,
        'selected_category': category,
        'selected_subject': subject_id,
        'selected_series': series_id,
        'total': qs.count(),
    }
    return render(request, 'resources/catalogue.html', context)


@require_POST
def upload_cover(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    img = request.FILES.get('cover_image')
    if not img:
        return JsonResponse({'error': 'No file received'}, status=400)
    resource.cover_image = img
    resource.save(update_fields=['cover_image'])
    return JsonResponse({'url': resource.cover_image.url})


def resource_detail(request, pk):
    resource = get_object_or_404(
        Resource.objects.prefetch_related('authors', 'subjects', 'copies', 'digital_files')
                        .select_related('publisher', 'series'),
        pk=pk
    )
    context = {
        'resource': resource,
        'available_copies': resource.copies.filter(status='AVAILABLE'),
        'other_copies': resource.copies.exclude(status='AVAILABLE'),
    }
    return render(request, 'resources/resource_detail.html', context)
