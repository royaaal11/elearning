from django import template
from emodule import configs

register = template.Library()

@register.filter
def emodule_pluralize(list_length, options):
    split_options = options.split(',')
    if list_length > 0:
        return split_options[1]
    else:
        return split_options[0]
    

@register.simple_tag
def emodule_status(status):
    if status is None or status == "":
        return None
    else:
        return status
    
@register.simple_tag
def emodule_score(score):
    if score is None or score == "":
        return None
    else:
        return score
    

@register.inclusion_tag("emodule/partial/badge.html")
def show_emodule_badge(quiz_or_assessment_list, status):
    return {
        "quiz_or_assessment_list": quiz_or_assessment_list, 
        "status": status    
    }