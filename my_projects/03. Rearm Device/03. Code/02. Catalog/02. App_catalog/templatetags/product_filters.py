from django import template
from django.db.models import Min, Max

from catalog.models import Product, Manufacture

register = template.Library()


@register.simple_tag
def get_manufacture():
    return Manufacture.objects.all()


@register.simple_tag(takes_context=True)
def get_prise(context):
    object_list = context['object_list']
    return object_list.aggregate(min_prise=Min('price'), max_prise=Max('price'))
