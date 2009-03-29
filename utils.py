import re

from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from django.shortcuts import render_to_response
from django.template import RequestContext

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
