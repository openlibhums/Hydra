from django.urls import re_path

from plugins.hydra import views

urlpatterns = [
    re_path(r'^$',
        views.index,
        name='hydra_index',
    ),
    re_path(
        r"^distribute/(?P<article_id>\d+)/$",
        views.distribute_articles_view,
        name="distribute_articles",
    ),
    re_path(
        r'articles/',
        views.hydra_handshake_url,
        name="hydra_handshake_url",
    ),
    re_path(
        r'article/(?P<article_id>\d+)/',
        views.hydra_jump_url,
        name="hydra_jump_url",
    ),
]
