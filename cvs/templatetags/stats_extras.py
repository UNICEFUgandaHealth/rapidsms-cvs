from django import template
from django.shortcuts import get_object_or_404
from simple_locations.models import Area
from django.core.exceptions import ObjectDoesNotExist

def get_section(path):
    pos = path.split('/')
    return pos[2]

def get_parent(location_id):
    if location_id:
        location = get_object_or_404(Area, pk=location_id)
    else:
        location = Area.tree.root_nodes()[0]
    return location

def get_parentId(location_id):
    if location_id:
        location = get_object_or_404(Area, pk=location_id)
    else:
        location = Area.tree.root_nodes()[0]
    return location.parent_id

def get_ancestors(location_id):
    if location_id:
        location = get_object_or_404(Area, pk=location_id)
    else:
        location = Area.tree.root_nodes()[0]
    return location.get_ancestors()

def name(location):
    return location.name

def latest(obj):
    try:
        return obj.default_connection.submissions.latest('created').created
    except ObjectDoesNotExist:
        return 'N/A'

register = template.Library()
register.filter('section', get_section)
register.filter('parent', get_parent)
register.filter('parentId', get_parentId)
register.filter('ancestors',get_ancestors)
register.filter('name', name)
register.filter('latest', latest)