from urllib.parse import urlparse

from django.db.models import Q, Subquery
from django.template.loader import render_to_string
from django.utils.translation import get_language_info

from plugins.hydra import models, utils
from utils.logger import get_logger

from utils import setting_handler


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
    normalised_path = stripped_path.lstrip("/")
    corrected_path = "/issues/" if normalised_path.startswith("issue/") else f"/{normalised_path}"

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
            parents_subq = models.LinkedArticle.objects.filter(
                    to_article=article
             ).values("from_article")

            linked_articles = models.LinkedArticle.objects.filter(
                Q(from_article=article) | Q(from_article__in=Subquery(parents_subq))
            ).exclude(to_article=article).select_related("to_article__journal")

            if not linked_articles.filter(to_article__journal=linked_journal).exists():
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


def editor_nav_article_switcher(context):
    """
    Adds backend links to linked articles.
    """
    request = context["request"]
    journal = getattr(request, "journal", None)
    article = context.get("article")

    sidebar_enabled = setting_handler.get_setting(
        "plugin:hydra",
        "hydra_enable_sidebar",
        journal=journal,
    ).processed_value

    if not sidebar_enabled:
        return ""

    if not article or not journal:
        return ""

    related = article.linked_from.select_related(
        "from_article__journal",
        "to_article__journal",
    ).all()
    related |= article.linked_to.select_related(
        "from_article__journal",
        "to_article__journal",
    ).all()

    linked_articles = utils.get_interlinked_articles(article.pk)
    linked_articles = {a for a in linked_articles if a.pk != article.pk}

    if not linked_articles:
        return ""

    current_code = journal.code
    links = []

    for a in linked_articles:
        raw_url = a.current_workflow_element_url or ""
        parsed = urlparse(raw_url)
        path_parts = parsed.path.strip("/").split("/")

        # If the current journal code appears early AND this is a *different* journal
        if (
            current_code in path_parts[:2]
            and a.journal_id != journal.pk
        ):
            path_parts = [part for part in path_parts if part != current_code]

        cleaned_path = "/" + "/".join(path_parts)

        links.append({
            "article": a,
            "journal": a.journal.code if hasattr(a, "journal") else "",
            "url": cleaned_path,
        })

    return render_to_string(
        "hydra/elements/linked_article_admin_links.html",
        {
            "article_links": links,
        }
    )


