from django import template
from jalali_date import date2jalali
from django.db.models import F,Sum
from accounts.models import Order, OrderDetail
register = template.Library()


@register.filter(name='cut')
def cut(value, arg):
    """Removes all values of arg from the given string"""
    return value.replace(arg, '')


@register.filter(name='show_jalali_date')
def show_jalali_date(value):
    return date2jalali(value)


@register.filter(name='three_digits_currency')
def three_digits_currency(value:int):
    return '{:,}'.format(value) + 'تومان'

@register.simple_tag
def multiply(quantity,price,*args,**kwargs):
    return quantity * price

