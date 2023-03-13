from django import template

register = template.Library()

@register.filter
def emodule_pluralize(list_length, options):
    split_options = options.split(',')
    if list_length > 0:
        return split_options[1]
    else:
        return split_options[0]