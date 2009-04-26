from django.conf import settings
from django.contrib.auth.models import User
from django.db import models, IntegrityError
from django.utils.translation import ugettext_lazy as _
from markdown.markdown import Markdown
import datetime

try:
    from tagging.models import Tag
    from tagging.fields import TagField
    from tagging.utils import taglist_to_string
    tagfield_help_text = _('Separate tags with spaces, put quotes around multiple-word tags.')

except ImportError:
    class TagField(models.CharField):
        def __init__(self, ** kwargs):
            default_kwargs = {'max_length': 255, 'blank': True}
            default_kwargs.update(kwargs)
            super(TagField, self).__init__( ** default_kwargs)
        def get_internal_type(self):
            return 'CharField'
    tagfield_help_text = _('Django-tagging was not found, tags will be treated as plain text.')


   
class Event(models.Model):
    """Event Model used to store data for one event.
    TODO: Cover Image?
          Attachements?
          Geocoding of the location
    """

    promoter = models.ForeignKey(User, related_name='events_promoted', blank=True, null=True)

    start_date = models.DateTimeField(_('Start date and time'), blank=True, null=True)
    end_date = models.DateTimeField(_('End date and time'), blank=True, null=True)
    image = models.ImageField(upload_to="events/%Y/%m/%d", blank=True, null=True)

    rsvp_link = models.URLField(_('RSVP Link'), blank=True, null=True, help_text=_('You can enter a link to a site where people can sign up for the event. Example: meetup.com or facebook.com'))

    # Location:
    location_address_1 = models.CharField(_('Address Line 1'), max_length=100, null=True, blank=True)   
    location_address_2 = models.CharField(_('Address Line 2'), max_length=100, null=True, blank=True)
    location_zip = models.CharField(_('ZIP Code'), max_length=10, null=True, blank=True)
    location_city = models.CharField(_('City'), max_length=30, null=True, blank=True)
    location_province = models.CharField(_('Region/Province/State'), max_length=30, null=True, blank=True)
    location_country = models.CharField(_('Country'), max_length=30, null=True, blank=True)

    tags = TagField()
    

    name = models.CharField(max_length=200)
    slug = models.SlugField(null=True, blank=True, unique=True)            
    description_html = models.TextField(blank=True)
    description_markdown = models.TextField(blank=True)
    location_short_name = models.CharField(max_length=100, blank=True, null=True)
    
    date_created = models.DateTimeField(blank=True, auto_now_add=True)    
    is_published = models.BooleanField(blank=True, default=True)    

    def __unicode__(self):
        FORMAT = '%d/%m/%Y %H:%M '
        return u"%s (%s - %s)" % (self.name, self.start_date.strftime(FORMAT), self.end_date.strftime(FORMAT))
 
    @models.permalink
    def get_absolute_url(self):
        return ('eventapp_view_event', (), {
            'year': self.start_date.year,
            'month': '%02d' % self.start_date.month,
            'day': '%02d' % self.start_date.day,
            'slug':self.slug
            }
            )

    def get_editable_tags(self):
        return taglist_to_string(self.get_tags())

    def set_tags(self, tags):
        return Tag.objects.update_tags(self, tags)
       
    def get_tags(self):
        return Tag.objects.get_for_object(self)

    def is_expired(self):
        return self.end_date < datetime.datetime.now()

    def get_comments(self):
        return Comment.objects.filter(event=self)

    def save(self):
        """Auto-populate an empty slug field from the Category name and
        if it conflicts with an existing slug then append a number and try
        saving again.
        """
        import re
        from django.template.defaultfilters import slugify
        
        if not self.slug:
            self.slug = slugify(self.name)  # Where self.name is the field used for 'pre-populate from'

        md = Markdown(safe_mode = True)
        self.description_html = md.convert(self.description_markdown)

        while True:
            try:
                super(Event, self).save()
            # Assuming the IntegrityError is due to a slug fight
            except IntegrityError:
                match_obj = re.match(r'^(.*)-(\d+)$', self.slug)
                if match_obj:
                    next_int = int(match_obj.group(2)) + 1
                    self.slug = match_obj.group(1) + '-' + str(next_int)
                else:
                    self.slug += '-2'
            else:
                break

class Comment(models.Model):
    text = models.CharField(max_length=5000, blank=False)
    text_html = models.CharField(max_length=5000, blank=True) # only for admin reasons is blank=True

    author = models.ForeignKey(User, related_name='comment_author')
    event = models.ForeignKey(Event)
    pub_date = models.DateTimeField(auto_now_add=True)
    # blank and null is for Django admin
    flagged_by = models.ManyToManyField(User, related_name='comment_flagged_by', blank=True, null=True)

    def save(self):
        md = Markdown(safe_mode=True)
        self.text_html = md.convert(self.text)
        super(Comment, self).save()

    @staticmethod
    def search(self, terms):
        query = get_query(terms, ['text',])
        return Comment.objects.filter(query)

    def get_edit_url(self):
        return '/events/editcomment/' + str(self.pk) + '/'
