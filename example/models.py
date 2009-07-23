from django.db import models

from feincms.module.blog.models import Entry, EntryAdmin
from feincms.module.page.models import Page
from feincms.content.raw.models import RawContent
from feincms.content.image.models import ImageContent
from feincms.content.medialibrary.models import MediaFileContent

Page.register_templates({
    'key': 'base',
    'title': 'Base Template',
    'path': 'base.html',
    'preview_image': '/media/template_base_preview.png',
    'regions': (
        ('main', 'Main region'),
        ('sidebar', 'Sidebar', 'inherited'),
        ),
    })
Page.create_content_type(RawContent)
MediaFileContent.default_create_content_type(Page)
Page.create_content_type(ImageContent, POSITION_CHOICES=(
    ('default', 'Default position'),
    ))


Entry.register_regions(
    ('main', 'Main region'),
    )
Entry.create_content_type(RawContent)
Entry.create_content_type(ImageContent, POSITION_CHOICES=(
    ('default', 'Default position'),
    ))


class Category(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField()

    class Meta:
        ordering = ['name']
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __unicode__(self):
        return self.name


# add m2m field to entry so it shows up in entry admin
Entry.add_to_class('categories', models.ManyToManyField(Category, blank=True, null=True))
EntryAdmin.list_filter += ('categories',)
