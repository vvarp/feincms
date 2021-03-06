from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from feincms import settings


class RichTextContent(models.Model):
    feincms_item_editor_context_processors = ( lambda x: dict(TINYMCE_JS_URL = settings.TINYMCE_JS_URL), )
    feincms_item_editor_includes = {
        'head': ['admin/content/richtext/init.html'],
        }

    text = models.TextField(_('text'), blank=True)

    class Meta:
        abstract = True
        verbose_name = _('rich text')
        verbose_name_plural = _('rich texts')

    def render(self, **kwargs):
        return mark_safe(self.text)

