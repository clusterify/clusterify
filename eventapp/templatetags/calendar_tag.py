#!/usr/bin/env python
from datetime import date, timedelta

from django import template
from eventapp.models import Event
import datetime

register = template.Library()


from datetime import date, timedelta

def event_count():
    return Event.objects.all().count()

register.simple_tag(event_count)

def get_last_day_of_month(year, month):
    if (month == 12):
        year += 1
        month = 1
    else:
        month += 1
    return date(year, month, 1) - timedelta(1)


def month_cal(year, month):
    event_list = Event.objects.filter(start_date__year=year,start_date__month=month)
    #event_list = []
    #for i in tmp_list:
    #    if i.start.year == year and i.start.month == month:
    #        event_list.append(i)
    first_day_of_month = date(year, month, 1)
    last_day_of_month = get_last_day_of_month(year, month)
    first_day_of_calendar = first_day_of_month - timedelta(first_day_of_month.weekday())
    last_day_of_calendar = last_day_of_month + timedelta(7 - last_day_of_month.weekday())

    month_cal = []
    week = []
    week_headers = []

    i = 0
    day = first_day_of_calendar
    while day <= last_day_of_calendar:
        if i < 7:
            week_headers.append(day)
        cal_day = {}
        cal_day['day'] = day
        cal_day['event'] = False
        for event in event_list:
            #if day == event.start.date():
            if day >= event.start_date.date() and day <= event.end_date.date():
                cal_day['event'] = True
                cal_day['slug'] = event.slug
        if day.month == month:
            cal_day['in_month'] = True
        else:
            cal_day['in_month'] = False  
        week.append(cal_day)
        if day.weekday() == 6:
            month_cal.append(week)
            week = []
        i += 1
        day += timedelta(1)
    return {'calendar': month_cal, 'headers': week_headers}

register.inclusion_tag('calendar.html')(month_cal)


def upcoming_event_count():
    return Event.objects.filter(end_date__gte = datetime.datetime.now()).count()

register.simple_tag(upcoming_event_count)

def past_event_count():
    return Event.objects.filter(end_date__lte = datetime.datetime.now()).count()

register.simple_tag(past_event_count)
