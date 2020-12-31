from django import template 

register = template.Library()


@register.filter(name='split')
def split(value, key):
    """
        Returns the value turned into a list.
    """
    return value.split(key)


@register.filter(name='getIx')
def getIx(h, key):
    return h[key]


@register.filter
def index(indexable, i):
    return indexable[i]


@register.filter
def id(obj):
    return obj.id

