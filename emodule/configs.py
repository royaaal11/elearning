from django.urls import reverse_lazy

# TODO: Implement dynamic menu config
MENU_CONFIG = [
    {
        "name": "Home",
        "url": reverse_lazy("emodule:home"),
        "sub_menu": {}
    },
    {
        "name": "Subjects",
        "url": reverse_lazy("emodule:subjects"),
        "sub_menu": {
            "name": "T.L.E",
            "url": "subject-detail",
            "sub_menu": {}
        }
    }
]

BREAD_CRUMB_BASE_CONFIG = ["Home"]


ACTIVITY_STATUS = (
    ("Passed", "Passed"),
    ("Failed", "Failed"),
)