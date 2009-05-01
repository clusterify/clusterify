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

import datetime
import math
import string

from django.db import models
from django.contrib.auth.models import User
from eventapp.models import Event

from markdown.markdown import Markdown

from tagging.fields import TagField
from tagging.models import Tag
from tagging.utils import taglist_to_string

from clusterify.utils import get_query

#### Constants

REFERENCE_DATE_FOR_SCORE = datetime.datetime(2008, 1, 1, 0, 0, 0)

# In Reddit formula, as per Aneesh's original comment(isn't the world small?)
# http://news.ycombinator.com/item?id=231188
# that was 45000, so ~12.5 hours. That means every 12.5 hours going by substracted as much as the
# first 10 votes, the next 90, the next 900... on a story submitted.
# In our case, we probably want good ideas to disappear much more slowly,
# and give more weight to votes.
DAMP_FACTOR_FOR_TIMEDELTA = 3600*24*3


####

class Project(models.Model):
	title = models.CharField(max_length=200)
	
	'''
	- proposed_by is always set to the original poster id, and never changes
	- author is the project admin. This can change or be null.
	
	- author = None, looking_for_admin = True: can happen if the proposer was anonymous.
	- author = x, looking_for_admin = False
	- author = x, looking_for_admin = True : temporary admin, 
			the user can act as an admin but anyone can take his place anytime
	
	- author = None, looking_for_admin = False: IMPOSSIBLE, MUST NOT HAPPEN
	
	Don't worry about wont_be_completed: if it's set, then looking_for_admin = False.
	'''
	author = models.ForeignKey(User, related_name='projects_authored', blank=True, null=True)
	proposed_by = models.ForeignKey(User, related_name='projects_proposed')
	looking_for_admin = models.BooleanField(default=False)
	
	description_html = models.TextField(blank=True)
	description_markdown = models.TextField(blank=True)
	
	showcase_html = models.TextField(blank=True)
	showcase_markdown = models.TextField(blank=True)
	
	hour_estimate = models.PositiveIntegerField(default=2)
	
	event = models.ForeignKey(Event, related_name='projects_event', blank=True, default=False)
	
	# set manually
	pub_date = models.DateTimeField(auto_now_add=False, auto_now=False)
	p_completed = models.BooleanField(default=False)
	wont_be_completed = models.BooleanField(default=False)
	
	proposed_votes = models.ManyToManyField(User, related_name='projects_proposed_votes', blank=True, null=True)
	completed_votes = models.ManyToManyField(User, related_name='projects_completed_votes', blank=True, null=True)
	
	# Using ManyToMany fields to record votes so we know who voted for what, if only to check if a user already voted
	#proposed_votes = models.PositiveIntegerField(default=1)
	#completed_votes = models.PositiveIntegerField(default=1)
	
	#interested_users = models.ManyToManyField(User, related_name='projects_interested', blank=True, null=True)
	#joined_users = models.ManyToManyField(User, related_name='projects_joined', blank=True, null=True)
	members = models.ManyToManyField(User, through='Membership')
	
	score_proposed = models.FloatField(default=0.0)
	score_completed = models.FloatField(default=0.0)
	
	# Using Tag.objects directly, instead of the field, now (otherwise
	# the field overwrites with empty tag list when we do .save())
	#tags = TagField()
	
	def __unicode__(self):
		return u'%s' %(self.title)

	def save(self):
		if not self.pk:
			self.pub_date = datetime.datetime.now()
		md = Markdown(safe_mode = True)
		self.description_html = md.convert(self.description_markdown)
		self.showcase_html = md.convert(self.showcase_markdown)
		super(Project, self).save()
	
	@staticmethod
	def search(terms):
		query = get_query(terms, ['title', 'description_markdown',])
		return Project.objects.filter(query)
	
	def get_comments(self):
		return Comment.objects.filter(project=self)

	##########################################################################
	# URLs

	def get_absolute_url(self):
		return "/projects/list/%s/%s/" %(self.author.username, str(self.pk))
	
	def get_postcomment_url(self):
		return "/projects/list/%s/%s/postcomment/" %(self.author.username, str(self.pk))
	
	def get_editing_url(self):
		return "/projects/list/%s/%s/edit/" %(self.author.username, str(self.pk))
		

	
	##########################################################################
	# Tag setting & getting
	
	# The set_tags functions must be called AFTER the object has been saved,
	# as otherwise the pk is not set yet

	def get_editable_tags(self):
		return taglist_to_string(self.get_tags())
	
	def set_tags(self, tags):
		return Tag.objects.update_tags(self, tags)
	
	def get_tags(self):
		return Tag.objects.get_for_object(self)


	##########################################################################
	# Joining

	def get_joined_users(self):
		return [m.user for m in Membership.objects.filter(project=self, approved=True)]

	def get_interested_users(self):
		return [m.user for m in Membership.objects.filter(project=self, approved=False)]

	# The add_user functions must be called AFTER the object has been saved
	def add_interested_user(self, user, role=''):
		if not self.p_completed:
			#self.interested_users.add(user)
			if Membership.objects.filter(project=self, user=user).count() == 0:
				Membership(project=self, user=user, role=role, approved=False).save()

	# used when a user moves from "Interested" to "Member" on a project
	def remove_member(self, user):
		m = Membership.objects.filter(project=self, user=user)
		m.delete()
		#self.interested_users.remove(user)

	def get_interested_users_count(self):
		return Membership.objects.filter(project=self, approved=False).count()

	def join_user(self, user, role=''):
		if not self.p_completed:
			try:
				m = Membership.objects.get(project=self, user=user)
				m.approved = True
				m.save()
			except Membership.DoesNotExist:
				Membership(project=self, user=user, role=role, approved=True).save()

	def get_joined_users_count(self):
		return Membership.objects.filter(project=self, approved=True).count()

	# Given a user, returns the user's position in the project 
	# (Author, Member, Interested, None)
	def join_status(self, user):
		if user == self.author:
			return "Author"
		elif user in self.get_joined_users():
			return "Member"
		elif user in self.get_interested_users():
			return "Interested"
		else:
			return "None"
	
	def member_role(self, user):
		m = Membership.objects.filter(project=self, user=user)
		
		if m.count() > 0:
			return m[0].role

	##########################################################################
	# Voting and score
	
	def add_proposed_vote(self, user):
		if self.user_voted_proposed(user):
			return self.proposed_votes.count()
		
		self.proposed_votes.add(user)
		self.update_proposed_score()
		
		self.author.get_profile().add_to_proposed_projects_karma(1)
		return self.proposed_votes.count()
	
	def add_completed_vote(self, user):
		if self.user_voted_completed(user):
			raise Exception('User already voted.')
		
		self.completed_votes.add(user)
		self.update_completed_score()
		
		# TODO: block users from joining after project is complete
		self.author.get_profile().add_to_completed_projects_karma(1)
		for u in self.get_joined_users():
			u.get_profile().add_to_completed_projects_karma(1)
		
	def user_voted_proposed(self, user):
		count = Project.objects.filter(pk=self.pk, proposed_votes__id__exact=user.pk).count()
		
		return count > 0
	
	def user_voted_completed(self, user):
		count = Project.objects.filter(pk=self.pk, completed_votes__id__exact=user.pk).count()
		
		return count > 0
	
	def get_score_given_count(self, vote_count):
		now = datetime.datetime.now()
		delta = now - REFERENCE_DATE_FOR_SCORE
		delta = delta.days * 3600 * 24 + delta.seconds
		return math.log(vote_count) + delta / DAMP_FACTOR_FOR_TIMEDELTA
	
	def update_proposed_score(self):
		self.score_proposed = self.get_score_given_count(self.proposed_votes.count())
		self.save()
	
	def update_completed_score(self):
		self.score_completed = self.get_score_given_count(self.completed_votes.count())
		self.save()

class Project_Proposed_Votes(models.Model):
	user = models.ForeignKey(User, unique=True)
	project = models.ForeignKey(Project, unique=True)

	def __unicode__(self):
		return u'%s, %s, %s' %(self.user, self.project.id, self.project)

class Comment(models.Model):
	text = models.CharField(max_length=5000, blank=False)
	text_html = models.CharField(max_length=5000, blank=True) # only for admin reasons is blank=True
	
	author = models.ForeignKey(User)
	project = models.ForeignKey(Project)
	pub_date = models.DateTimeField(auto_now_add=True)
	# blank and null is for Django admin
	flagged_by = models.ManyToManyField(User, related_name='flagged_by', blank=True, null=True)

	def save(self):
		md = Markdown(safe_mode = True)
		self.text_html = md.convert(self.text)
		super(Comment, self).save()

	@staticmethod
	def search(terms):
		query = get_query(terms, ['text',])
		return Comment.objects.filter(query)

	def get_edit_url(self):
		return self.project.get_absolute_url() + 'editcomment/' + str(self.pk) + '/'



class Membership(models.Model):
	user = models.ForeignKey(User)
	project = models.ForeignKey(Project)
	role = models.CharField(max_length=120, blank=True)
	approved = models.BooleanField(default=False)
