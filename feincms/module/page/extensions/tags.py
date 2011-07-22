from django.utils.translation import ugettext_lazy as _

def register(cls, admin_cls):
    try:
        from taggit.managers import TaggableManager
        cls.add_to_class('tags', TaggableManager(blank=True))
    except ImportError:
        from tagging.fields import TagField
        cls.add_to_class('tags', TagField(_('Tags')))
 