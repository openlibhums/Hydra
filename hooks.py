from itertools import groupby
from operator import attrgetter

from django.db.models import Q, Subquery
from django.apps import apps
from django.template.loader import render_to_string
from django.utils.translation import get_language_info

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


def language_header_switcher(context):
    """
    Provides a language switcher for linked journal sites.
    """

    request = context["request"]
    journal = getattr(request, "journal", None)
    article = context.get("article")
    path = request.path

    if not journal:
        return ""

    # Find the linked group this journal belongs to
    try:
        linked_group = journal.linked_journals
    except models.LinkedJournals.DoesNotExist:
        try:
            linked_group = models.LinkedJournals.objects.get(links=journal)
        except models.LinkedJournals.DoesNotExist:
            return ""

    if not linked_group.journal_link.exists():
        return ""

    # Strip the journal-specific path prefix
    prefix = f"/{journal.code}/"
    stripped_path = path[len(prefix):] if path.startswith(prefix) else path
    corrected_path = "/issues/" if stripped_path.startswith("issue/") else f"/{stripped_path}"

    # Build the full set of group journals
    group_journals = {linked_group.journal}
    group_journals.update(
        link.to_journal for link in linked_group.journal_link.select_related("to_journal")
    )

    links = []

    for linked_journal in group_journals:
        if linked_journal.pk == journal.pk:
            continue

        try:
            linked_language = linked_journal.get_setting(
                group_name="general",
                setting_name="default_journal_language",
            )
        except Exception:
            continue

        if article:
            related = article.linked_from.select_related("from_article__journal", "to_article__journal").all()
            related |= article.linked_to.select_related("from_article__journal", "to_article__journal").all()
            if not any(
                a.to_article.journal_id == linked_journal.pk
                or a.from_article.journal_id == linked_journal.pk
                for a in related
            ):
                continue

        links.append({
            "name_local": get_language_info(linked_language)["name_local"],
            "url": linked_journal.site_url(path=corrected_path),
        })

    if not links:
        return ""

    return render_to_string(
        "hydra/elements/language_links.html",
        {
            "language_links": links,
        }
    )
