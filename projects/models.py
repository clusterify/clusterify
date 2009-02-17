import datetime
import math
import string

from django.db import models
from django.contrib.auth.models import User

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
	
	author = models.ForeignKey(User, related_name='projects_authored')
	
	description_html = models.TextField(blank=True)
	description_markdown = models.TextField(blank=True)
	
	showcase_html = models.TextField(blank=True)
	showcase_markdown = models.TextField(blank=True)
	
	hour_estimate = models.PositiveIntegerField(default=2)
	
	# set manually
	pub_date = models.DateTimeField(auto_now_add=False, auto_now=False)
	p_completed = models.BooleanField(default=False)

	proposed_votes = models.ManyToManyField(User, related_name='projects_proposed_votes', blank=True, null=True)
	completed_votes = models.ManyToManyField(User, related_name='projects_completed_votes', blank=True, null=True)

	# Using ManyToMany fields to record votes so we know who voted for what, if only to check if a user already voted
	#proposed_votes = models.PositiveIntegerField(default=1)
	#completed_votes = models.PositiveIntegerField(default=1)
	
	interested_users = models.ManyToManyField(User, related_name='projects_interested', blank=True, null=True)
	joined_users = models.ManyToManyField(User, related_name='projects_joined', blank=True, null=True)
	
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
	
	# To be called BEFORE setting required tags, for them to take precedence
	
	#def set_description_tags(self, tags_string):
	#	Tag.objects.add_tags_with_weight(self, tags_string, 0)
	
	#def set_required_tags(self, tags_string):
	#	Tag.objects.add_tags_with_weight(self, tags_string, 1)
	
	#def get_required_tags(self):
	#	return Tag.objects.get_tags_with_weight(self, 1)
	
	#def get_description_tags(self):
	#	return Tag.objects.get_tags_with_weight(self, 0)
	
	#def get_editable_desc_tags(self):
	#	return taglist_to_string(self.get_description_tags())
	
	#def get_editable_reqd_tags(self):
	#	return taglist_to_string(self.get_required_tags())
	
	def get_editable_tags(self):
		return taglist_to_string(self.get_tags())
	
	def set_tags(self, tags):
		return Tag.objects.update_tags(self, tags)
	
	def get_tags(self):
		return Tag.objects.get_for_object(self)


	##########################################################################
	# Joining

	# The add_user functions must be called AFTER the object has been saved
	def add_interested_user(self, user):
		if not self.p_completed:
			self.interested_users.add(user)

	# used when a user moves from "Interested" to "Member" on a project
	def remove_interested_user(self, user):
		self.interested_users.remove(user)

	def get_interested_users_count(self):
		self.interested_users.count()

	def join_user(self, user):
		if not self.p_completed:
			self.joined_users.add(user)

	def get_joined_users_count(self):
		return self.joined_users.count() + 1

	# Given a user, returns the user's position in the project 
	# (Author, Member, Interested, None)
	def join_status(self, user):
		if user == self.author:
			return "Author"
		elif user in self.joined_users.all():
			return "Member"
		elif user in self.interested_users.all():
			return "Interested"
		else:
			return "None"

	##########################################################################
	# Voting and score
	
	def add_proposed_vote(self, user):
		if self.user_voted_proposed(user):
			raise Exception('User already voted.')
		
		self.proposed_votes.add(user)
		self.update_proposed_score()
		
		self.author.get_profile().add_to_proposed_projects_karma(1)

	def add_completed_vote(self, user):
		if self.user_voted_completed(user):
			raise Exception('User already voted.')
		
		self.completed_votes.add(user)
		self.update_completed_score()
		
		# TODO: block users from joining after project is complete
		self.author.get_profile().add_to_completed_projects_karma(1)
		for u in self.joined_users.all():
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

class Comment(models.Model):
	text = models.CharField(max_length=5000)
	author = models.ForeignKey(User)
	project = models.ForeignKey(Project)
	pub_date = models.DateTimeField(auto_now_add=True)
	# blank and null is for Django admin
	flagged_by = models.ManyToManyField(User, related_name='flagged_by', blank=True, null=True)

	@staticmethod
	def search(terms):
		query = get_query(terms, ['text',])
		return Comment.objects.filter(query)

