import datetime
import random
import re
import sha

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from tagging.fields import TagField
from tagging.models import Tag
from tagging.utils import taglist_to_string

from markdown.markdown import Markdown

from clusterify.utils import get_query

import urllib, hashlib 

SHA1_RE = re.compile('^[a-f0-9]{40}$')

# NOTE: the code of django-registration was heavily modified...
# it almost isn't used anymore, due to the bypass of the activation email process



##############################################################################
# Mostly the original django-registration code

class RegistrationManager(models.Manager):
    """
    Custom manager for the ``RegistrationProfile`` model.
    
    The methods defined here provide shortcuts for account creation
    and activation (including generation and emailing of activation
    keys), and for cleaning out expired inactive accounts.
    
    """
    def activate_user(self, activation_key):
        """
        Validate an activation key and activate the corresponding
        ``User`` if valid.
        
        If the key is valid and has not expired, return the ``User``
        after activating.
        
        If the key is not valid or has expired, return ``False``.
        
        If the key is valid but the ``User`` is already active,
        return ``False``.
        
        To prevent reactivation of an account which has been
        deactivated by site administrators, the activation key is
        reset to the string constant ``RegistrationProfile.ACTIVATED``
        after successful activation.

        To execute customized logic when a ``User`` is activated,
        connect a function to the signal
        ``registration.signals.user_activated``; this signal will be
        sent (with the ``User`` as the value of the keyword argument
        ``user``) after a successful activation.
        
        """
        from registration.signals import user_activated
        
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not profile.activation_key_expired():
                user = profile.user
                user.is_active = True
                user.save()
                profile.activation_key = self.model.ACTIVATED
                profile.save()
                user_activated.send(sender=self.model, user=user)
                
                # MODIF: create the Profile object too
                user_profile = Profile(user=user)
                user_profile.save()
                
                return user
        return False
    
    def create_inactive_user(self, username, password, email,
                             send_email=True):
        """
        Create a new, inactive ``User``, generate a
        ``RegistrationProfile`` and email its activation key to the
        ``User``, returning the new ``User``.
        
        To disable the email, call with ``send_email=False``.

        The activation email will make use of two templates:

        ``registration/activation_email_subject.txt``
            This template will be used for the subject line of the
            email. It receives one context variable, ``site``, which
            is the currently-active
            ``django.contrib.sites.models.Site`` instance. Because it
            is used as the subject line of an email, this template's
            output **must** be only a single line of text; output
            longer than one line will be forcibly joined into only a
            single line.

        ``registration/activation_email.txt``
            This template will be used for the body of the email. It
            will receive three context variables: ``activation_key``
            will be the user's activation key (for use in constructing
            a URL to activate the account), ``expiration_days`` will
            be the number of days for which the key will be valid and
            ``site`` will be the currently-active
            ``django.contrib.sites.models.Site`` instance.

        To execute customized logic once the new ``User`` has been
        created, connect a function to the signal
        ``registration.signals.user_registered``; this signal will be
        sent (with the new ``User`` as the value of the keyword
        argument ``user``) after the ``User`` and
        ``RegistrationProfile`` have been created, and the email (if
        any) has been sent..
        
        """
        from registration.signals import user_registered

        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.save()
        
        registration_profile = self.create_profile(new_user)
        
        if send_email:
            from django.core.mail import send_mail
            current_site = Site.objects.get_current()
            
            subject = render_to_string('registration/activation_email_subject.txt',
                                       { 'site': current_site })
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            
            message = render_to_string('registration/activation_email.txt',
                                       { 'activation_key': registration_profile.activation_key,
                                         'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                                         'site': current_site })
            
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [new_user.email])
        user_registered.send(sender=self.model, user=new_user)
        return new_user
    create_inactive_user = transaction.commit_on_success(create_inactive_user)
    
    def create_profile(self, user):
        """
        Create a ``RegistrationProfile`` for a given
        ``User``, and return the ``RegistrationProfile``.
        
        The activation key for the ``RegistrationProfile`` will be a
        SHA1 hash, generated from a combination of the ``User``'s
        username and a random salt.
        
        """
        salt = sha.new(str(random.random())).hexdigest()[:5]
        activation_key = sha.new(salt+user.username).hexdigest()
        return self.create(user=user,
                           activation_key=activation_key)
        
    def delete_expired_users(self):
        """
        Remove expired instances of ``RegistrationProfile`` and their
        associated ``User``s.
        
        Accounts to be deleted are identified by searching for
        instances of ``RegistrationProfile`` with expired activation
        keys, and then checking to see if their associated ``User``
        instances have the field ``is_active`` set to ``False``; any
        ``User`` who is both inactive and has an expired activation
        key will be deleted.
        
        It is recommended that this method be executed regularly as
        part of your routine site maintenance; this application
        provides a custom management command which will call this
        method, accessible as ``manage.py cleanupregistration``.
        
        Regularly clearing out accounts which have never been
        activated serves two useful purposes:
        
        1. It alleviates the ocasional need to reset a
           ``RegistrationProfile`` and/or re-send an activation email
           when a user does not receive or does not act upon the
           initial activation email; since the account will be
           deleted, the user will be able to simply re-register and
           receive a new activation key.
        
        2. It prevents the possibility of a malicious user registering
           one or more accounts and never activating them (thus
           denying the use of those usernames to anyone else); since
           those accounts will be deleted, the usernames will become
           available for use again.
        
        If you have a troublesome ``User`` and wish to disable their
        account while keeping it in the database, simply delete the
        associated ``RegistrationProfile``; an inactive ``User`` which
        does not have an associated ``RegistrationProfile`` will not
        be deleted.
        
        """
        for profile in self.all():
            if profile.activation_key_expired():
                user = profile.user
                if not user.is_active:
                    user.delete()


class RegistrationProfile(models.Model):
    """
    A simple profile which stores an activation key for use during
    user account registration.
    
    Generally, you will not want to interact directly with instances
    of this model; the provided manager includes methods
    for creating and activating new accounts, as well as for cleaning
    out accounts which have never been activated.
    
    While it is possible to use this model as the value of the
    ``AUTH_PROFILE_MODULE`` setting, it's not recommended that you do
    so. This model's sole purpose is to store data temporarily during
    account registration and activation.
    
    """
    ACTIVATED = u"ALREADY_ACTIVATED"
    
    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    activation_key = models.CharField(_('activation key'), max_length=40)
    
    objects = RegistrationManager()
    
    class Meta:
        verbose_name = _('registration profile')
        verbose_name_plural = _('registration profiles')
    
    def __unicode__(self):
        return u"Registration information for %s" % self.user
    
    def activation_key_expired(self):
        """
        Determine whether this ``RegistrationProfile``'s activation
        key has expired, returning a boolean -- ``True`` if the key
        has expired.
        
        Key expiration is determined by a two-step process:
        
        1. If the user has already activated, the key will have been
           reset to the string constant ``ACTIVATED``. Re-activating
           is not permitted, and so this method returns ``True`` in
           this case.

        2. Otherwise, the date the user signed up is incremented by
           the number of days specified in the setting
           ``ACCOUNT_ACTIVATION_DAYS`` (which should be the number of
           days after signup during which a user is allowed to
           activate their account); if the result is less than or
           equal to the current date, the key has expired and this
           method returns ``True``.
        
        """
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == self.ACTIVATED or \
               (self.user.date_joined + expiration_date <= datetime.datetime.now())
    activation_key_expired.boolean = True









##############################################################################
# THE FOLLOWING LICENSE APPLIES TO THE REST OF THIS FILE
# (the rest of this file contains additions made to the original
# django-registration module for Clusterify)

"""
"The contents of this file are subject to the Common Public Attribution
License Version 1.0 (the "License"); you may not use this file except 
in compliance with the License. You may obtain a copy of the License at 
http://www.clusterify.com/files/CODE_LICENSE.txt. The License is based 
on the Mozilla Public License Version 1.1 but Sections 14 and 15 have 
been added to cover use of software over a computer network and provide 
for limited attribution for the Original Developer. In addition, Exhibit 
A has been modified to be consistent with Exhibit B.

Software distributed under the License is distributed on an "AS IS" basis, 
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License 
for the specific language governing rights and limitations under the 
License.

The Original Code is Clusterify.

The Initial Developer of the Original Code is "the Clusterify.com team", 
which is described at http://www.clusterify.com/about/. All portions of 
the code written by the Initial Developer are Copyright (c) the Initial 
Developer. All Rights Reserved.
"""

def get_gravatar_image_url(email):
	# Set your variables here
	default = ""
	size = 50
	
	# construct the url  
	gravatar_url = "http://www.gravatar.com/avatar.php?"  
	gravatar_url += urllib.urlencode({'gravatar_id':hashlib.md5(email.lower()).hexdigest(), 'default':'identicon', 'size':str(size)})
	
	return gravatar_url

class OpenIdAssociation(models.Model):
	user = models.ForeignKey(User)
	# TODO: make this unique
	url = models.URLField(blank=False)

# Inspired by http://code.google.com/p/django-openid-auth/source/browse/trunk/openid_auth/models.py
# add registration.models.OpenIdBackend to settings.AUTHENTICATION_BACKENDS
# see http://docs.djangoproject.com/en/dev/topics/auth/#writing-an-authentication-backend
class OpenIdBackend:
    def authenticate(self, openid_url=None):
        if openid_url:
            try:
                user_openid = OpenIdAssociation.objects.get(url=openid_url)
                return user_openid.user
            except OpenIdAssociation.DoesNotExist:
                return None
        else:
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

# MODIF: added this class, should be set as AUTH_PROFILE_MODULE
class Profile(models.Model):
	user = models.ForeignKey(User, unique=True)
	
	description_markdown = models.TextField(blank=True)
	description_html = models.TextField(blank=True)
	
	proposed_projects_karma = models.PositiveIntegerField(default=1)
	completed_projects_karma = models.PositiveIntegerField(default=1)
	comment_karma = models.PositiveIntegerField(default=1)
	
	location = models.TextField(blank=True)
	
	# Using Tag.objects directly, instead of the field, now (otherwise
	# the field overwrites with empty tag list when we do .save())
	#tags = TagField()
	
	def get_absolute_url(self):
		return "/accounts/profile/view/%s/" % (self.user.username,)
	
	def save(self, *args, **kwargs):
		md = Markdown(safe_mode = True)
		self.description_html = md.convert(self.description_markdown)
		super(Profile, self).save()
		
	@staticmethod
	def search(terms):
		query = get_query(terms, ['description_markdown',])
		return Profile.objects.filter(query)
	
	def get_gravatar_url(self):
		return get_gravatar_image_url(self.user.email)
	
	##########################################################################
	# Tags
	
	def get_tags(self):
		return Tag.objects.get_for_object(self)
	
	def get_editable_tags(self):
		return taglist_to_string(self.get_tags())
	
	def set_tags(self, tags_string):
		Tag.objects.update_tags(self, tags_string)
	
	##########################################################################
	# Karma
	
	def add_to_proposed_projects_karma(self, num):
		self.proposed_projects_karma += num
		
		if self.proposed_projects_karma < 0:
			self.proposed_projects_karma = 0
			
		self.save()
		
	def add_to_completed_projects_karma(self, num):
		self.completed_projects_karma += num
		
		if self.completed_projects_karma < 0:
			self.completed_projects_karma = 0
			
		self.save()
		
	def add_to_commens_karma(self, num):
		self.comment_karma += num
		
		if self.comment_karma < 0:
			self.comment_karma = 0
			
		self.save()
		
		


