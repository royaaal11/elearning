from django import template
from django.template.defaultfilters import stringfilter

from emodule import configs

register = template.Library()

@register.filter
def emodule_pluralize(list_length, options):
    split_options = options.split(',')
    if list_length > 0:
        return split_options[1]
    else:
        return split_options[0]
    

@register.filter
@stringfilter
def template_exists(template_name):
    try:
        template.loader.get_template(template_name)
        return True
    except template.TemplateDoesNotExist:
        return False
    

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
    

@register.simple_tag
def get_assessment_button_text(latest_status, attempt_count, max_attempts):
    button_text = 'Take the assessment'
    if latest_status is not None:
        if latest_status == 'Passed':
            button_text = 'View result'
        else:
            if int(attempt_count) >= int(max_attempts):
                button_text = 'View result'
            else:
                button_text = 'Retake'

    else:
        return button_text
    
    return button_text


@register.simple_tag
def get_assessment_submit_button_class(latest_status, attempt_count, max_attempts):
    if latest_status is not None:
        if latest_status == 'Passed':
            return 'disabled'
        else:
            if int(attempt_count) >= int(max_attempts):
                return 'disabled'
            else:
                return None

    else:
        return None
    

@register.inclusion_tag("emodule/partial/badge.html")
def show_emodule_badge(quiz_or_assessment_list, status):
    return {
        "quiz_or_assessment_list": quiz_or_assessment_list, 
        "status": status    
    }
