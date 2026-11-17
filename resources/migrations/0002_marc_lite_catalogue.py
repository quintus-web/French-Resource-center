# Hand-edited migration to safely convert publisher CharField -> ForeignKey
# by migrating existing text values into Publisher rows first.

import django.db.models.deletion
from django.db import migrations, models


def migrate_publishers_forward(apps, schema_editor):
    Resource = apps.get_model('resources', 'Resource')
    Publisher = apps.get_model('resources', 'Publisher')
    for resource in Resource.objects.exclude(publisher_name='').exclude(publisher_name__isnull=True):
        publisher, _ = Publisher.objects.get_or_create(name=resource.publisher_name)
        resource.publisher = publisher
        resource.save(update_fields=['publisher'])


def migrate_publishers_backward(apps, schema_editor):
    Resource = apps.get_model('resources', 'Resource')
    for resource in Resource.objects.select_related('publisher'):
        if resource.publisher:
            resource.publisher_name = resource.publisher.name
            resource.save(update_fields=['publisher_name'])


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0001_initial'),
    ]

    operations = [
        # 1. Create new lookup tables
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('nationality', models.CharField(blank=True, max_length=100)),
                ('bio', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Author',
                'verbose_name_plural': 'Authors',
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('website', models.URLField(blank=True)),
            ],
            options={
                'verbose_name': 'Publisher',
                'verbose_name_plural': 'Publishers',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Series / Collection',
                'verbose_name_plural': 'Series / Collections',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'verbose_name': 'Subject',
                'verbose_name_plural': 'Subjects',
                'ordering': ['name'],
            },
        ),

        # 2. Rename old publisher CharField to publisher_name (preserve data)
        migrations.RenameField(
            model_name='resource',
            old_name='publisher',
            new_name='publisher_name',
        ),

        # 3. Add new publisher FK (nullable so existing rows are fine)
        migrations.AddField(
            model_name='resource',
            name='publisher',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='resources',
                to='resources.publisher',
            ),
        ),

        # 4. Data migration: create Publisher rows and point FK
        migrations.RunPython(migrate_publishers_forward, migrate_publishers_backward),

        # 5. Drop the old text field
        migrations.RemoveField(model_name='resource', name='publisher_name'),

        # 6. Remove old author CharField
        migrations.RemoveField(model_name='resource', name='author'),

        # 7. Add remaining new fields to BookCopy
        migrations.AddField(
            model_name='bookcopy',
            name='acquired_date',
            field=models.DateField(blank=True, help_text='Date this copy was added to the collection', null=True),
        ),
        migrations.AddField(
            model_name='bookcopy',
            name='acquisition_cost',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Purchase price in local currency', max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='bookcopy',
            name='acquisition_source',
            field=models.CharField(blank=True, choices=[('PURCHASED', 'Purchased'), ('DONATED', 'Donated'), ('GRANT', 'Grant / Aid'), ('TRANSFER', 'Transfer from Another Library'), ('OTHER', 'Other')], default='PURCHASED', max_length=15),
        ),
        migrations.AddField(
            model_name='bookcopy',
            name='donor_name',
            field=models.CharField(blank=True, help_text='Name of donor if applicable', max_length=255),
        ),

        # 8. Add remaining new fields to Resource
        migrations.AddField(
            model_name='resource',
            name='call_number',
            field=models.CharField(blank=True, db_index=True, help_text='Dewey Decimal or local call number (e.g. 448.2 DUM)', max_length=30),
        ),
        migrations.AddField(
            model_name='resource',
            name='cover_image',
            field=models.ImageField(blank=True, help_text='Front cover thumbnail', null=True, upload_to='covers/%Y/'),
        ),
        migrations.AddField(
            model_name='resource',
            name='edition',
            field=models.CharField(blank=True, help_text='e.g. 2nd Edition, Revised', max_length=50),
        ),
        migrations.AddField(
            model_name='resource',
            name='language',
            field=models.CharField(choices=[('FR', 'French'), ('FR_EN', 'French / English Bilingual'), ('EN', 'English (about French)'), ('OTHER', 'Other')], default='FR', max_length=10),
        ),
        migrations.AddField(
            model_name='resource',
            name='series_number',
            field=models.PositiveIntegerField(blank=True, help_text='Volume/part number within the series', null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='subtitle',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='resource',
            name='isbn',
            field=models.CharField(blank=True, db_index=True, help_text='ISBN-10 or ISBN-13', max_length=30),
        ),
        migrations.AddField(
            model_name='resource',
            name='authors',
            field=models.ManyToManyField(blank=True, related_name='resources', to='resources.author'),
        ),
        migrations.AddField(
            model_name='resource',
            name='series',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resources', to='resources.series'),
        ),
        migrations.AddField(
            model_name='resource',
            name='subjects',
            field=models.ManyToManyField(blank=True, related_name='resources', to='resources.subject'),
        ),
    ]
