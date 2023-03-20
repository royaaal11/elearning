from django.urls import reverse_lazy

ACTIVITY_STATUS = (
    ("Passed", "Passed"),
    ("Failed", "Failed"),
)

PASSING_PERCENTAGE = 60;

ALLOW_SAVE_TO_DB = True

# set as 'INFINITE' to allow endless retries
ASSESSMENT_MAX_ATTEMPTS = 3
