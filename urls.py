from django.urls import re_path

from plugins.hydra import views

urlpatterns = [
    re_path(r'^$',
        views.index,
        name='hydra_index',
    )
]
