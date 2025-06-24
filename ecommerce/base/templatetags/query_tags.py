from django import template

register = template.Library()

@register.filter
def get_item(queryset, index):
    try:
        return queryset[index]  # Returns None if index is out of bounds
    except (IndexError, TypeError):
        return None