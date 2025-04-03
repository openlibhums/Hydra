from itertools import groupby
from operator import attrgetter

from django.db.models import Q, Subquery
from django.apps import apps
from django.template.loader import render_to_string

from plugins.hydra import models
from utils.logger import get_logger


logger = get_logger(__name__)


def sidebar_article_links(context, article):
    """ Provides an HTML list of links to linked articles
    :param context: The context passed to the source template for rendering
    :type context: dict
    :param Article: The Article on which to match the pubid across journals
    :type Article: An instance of submission.models.Article
    """
    parents_subQ = models.LinkedArticle.objects.filter(
        to_article=article).values("from_article")
    # We want direct child relations or siblings via parent relationship 
    relatives = models.LinkedArticle.objects.filter(
        Q(from_article=article) | Q(from_article__in=Subquery(parents_subQ))
    ).exclude(to_article=article).distinct()
    if relatives.exists():
        return render_to_string(
            "hydra/elements/sidebar_links.html",
            {"relatives": relatives},
        )
    return ""
