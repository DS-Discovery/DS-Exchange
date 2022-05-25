from django import template 
from constance import config
from projects.models import Project

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


@register.filter
def addclass(field, css):
    old_css = field.field.widget.attrs.get("class", "")
    return field.as_widget(attrs={"class": old_css + " " + css})


@register.filter
def get_attr(obj, attr):
    return getattr(obj, attr)


@register.filter
def is_group_member(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.simple_tag
def current_semester():
    inv_sem_map = {v:k for k, v in Project.sem_mapping.items()}
    return inv_sem_map[config.CURRENT_SEMESTER]