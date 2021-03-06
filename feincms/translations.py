"""
Usage Example
=============

class News(models.Model, TranslatedObjectMixin):
    active = models.BooleanField(default=False)
    created = models.DateTimeField(default=datetime.now)


class NewsTranslation(Translation(News)):
    title = models.CharField(max_length=200)
    body = models.TextField()


# Print the titles of all news entries either in the current language (if available)
# or in any other language:
for news in News.objects.all():
    print news.translation.title

# Print all the titles of all news entries which have an english translation:
from django.utils import translation
translation.activate('en')
for news in News.objects.filter(translations__language_code='en'):
    print news.translation.title
"""

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.utils import translation


def short_language_code(code=None):
    """
    Extract the short language code from its argument (or return the default language code).
    
    from django.conf import settings
    >>> short_language_code('de')
    'de'
    >>> short_language_code('de-at')
    'de'
    >>> short_language_code() == short_language_code(settings.LANGUAGE_CODE)
    True
    """
    if code is None:
        code = translation.get_language()

    pos = code.find('-')
    if pos > -1:
        return code[:pos]
    return code


def is_primary_language(language=None):
    """
    Returns true if current or passed language is the primary language for this site.
    (The primary language is defined as the first language in settings.LANGUAGES.)
    """

    if not language:
        language = translation.get_language()

    return language == settings.LANGUAGES[0][0]


class TranslatedObjectManager(models.Manager):
    def only_language(self, language=short_language_code):
        return self.filter(translations__language_code=language)


class TranslatedObjectMixin(object):
    def _get_translation_object(self, queryset, language_code):
        try:
            return queryset.filter(
                Q(language_code=language_code)
                | Q(language_code=short_language_code(language_code))
                ).order_by('-language_code')[0]
        except IndexError:
            try:
                return queryset.filter(
                    Q(language_code__istartswith=settings.LANGUAGE_CODE)
                    | Q(language_code__istartswith=short_language_code(settings.LANGUAGE_CODE))
                    ).order_by('-language_code')[0]
            except IndexError:
                try:
                    return queryset.all()[0]
                except IndexError:
                    raise queryset.model.DoesNotExist

    def get_translation(self, language_code=None):
        if not language_code:
            language_code = translation.get_language()

        key = '-'.join(['%s' % s for s in
            self.__class__.__name__,
            self.id,
            language_code,
            ])

        trans = cache.get(key)

        if trans is None:
            trans = self._get_translation_object(self.translations.all(), language_code)
            cache.set(key, trans)

        return trans

    translation = property(get_translation)

    @property
    def available_translations(self):
        return self.translations.values_list('language_code', flat=True)

    def __unicode__(self):
        try:
            translation = self.translation
        except models.ObjectDoesNotExist:
            return self.__class__.__name__

        if translation:
            return unicode(translation)

        return self.__class__.__name__

    def get_absolute_url(self):
        return self.translation.get_absolute_url()


def Translation(model):
    """
    Return a class which can be used as inheritance base for translation models
    """

    class Inner(models.Model):
        parent = models.ForeignKey(model, related_name='translations')
        language_code = models.CharField(max_length=10, choices=settings.LANGUAGES)

        class Meta:
            abstract = True

        def short_language_code(self):
            return short_language_code(self.language_code)

    return Inner

