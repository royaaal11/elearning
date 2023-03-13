from .models import Subject

def base_context():
    return {
        "subject_list": Subject.objects.all()
    }

def update_context(context, new_context):
    context.update(new_context)
    return context