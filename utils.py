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

import re

from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib.sites.models import Site

def get_full_url(path_relative_to_site_root=""):
	return 'http://%s%s' % (Site.objects.get_current().domain, path_relative_to_site_root)

def oops(request, error_message=""):
	return render_to_response('oops.html',
		{'error_message': error_message},
		context_instance=RequestContext(request))

def generic_confirmation_view(request, question, url_yes, url_no):
	return render_to_response("confirm.html",
			{'question':question, 'url_yes':url_yes, 'url_no': url_no},
			context_instance=RequestContext(request))

# http://www.djangosnippets.org/snippets/41/
def get_request_url(request):
    full_path = ('http', ('', 's')[request.is_secure()], '://', request.META['HTTP_HOST'], request.path)
    return ''.join(full_path)


# Utility function to get page for Paginator
# see http://docs.djangoproject.com/en/dev/topics/pagination/
def get_paginator_page(request, obj_list, num_per_page):
	paginator = Paginator(obj_list, num_per_page)
	
	pagenum = 1
	
	try:
		pagenum = int(request.GET.get('page', '1'))
	except ValueError:
		pass
		
	try:
		return paginator.page(pagenum)
	except (EmptyPage, InvalidPage):
		# Return last page if index is higher than available
		return paginator.page(paginator.num_pages)

##############################################################################
# Simple search functionality for models

# Taken from http://www.julienphalip.com/blog/2008/08/16/adding-search-django-site-snap/
def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:
        
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    
    '''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query
