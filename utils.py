from django.core.management import call_command
from django.db.models import Q, Subquery

from plugins.hydra import models
from utils.function_cache import cache
from submission import models as submission_models


def get_linked_journals(article):
    journal = article.journal

    # Try direct access via reverse relation
    try:
        linked_group = journal.linked_journals
    except models.LinkedJournals.DoesNotExist:
        try:
            linked_group = models.LinkedJournals.objects.get(links=journal)
        except models.LinkedJournals.DoesNotExist:
            return

    # Build set of journals: primary + linked ones
    group_journals = {linked_group.journal}
    group_journals.update(
        link.to_journal for link in
        linked_group.journal_link.select_related("to_journal")
    )

    # Exclude the current journal
    group_journals.discard(journal)

    return group_journals


def distribute_articles(article, journals):
    for journal in journals:
        try:
            call_command(
                "copy_articles",
                journal.code,
                article=article.pk,
                stage="Editor Copyediting",
                target_lang="en",
            )
        except Exception as e:
            return e
    return None


@cache(600)
def get_interlinked_articles(article_id):
    """
    Return related articles: direct children and siblings via parent relationship.
    """
    try:
        article = submission_models.Article.objects.get(pk=article_id)
    except submission_models.Article.DoesNotExist:
        return set()

    parent_ids = models.LinkedArticle.objects.filter(
        to_article=article
    ).values("from_article")

    relatives = models.LinkedArticle.objects.filter(
        Q(from_article=article) | Q(from_article__in=Subquery(parent_ids))
    ).select_related(
        "from_article__journal",
        "to_article__journal",
    ).distinct()

    linked_articles = set()

    for link in relatives:
        if link.from_article and link.from_article.pk != article.pk:
            linked_articles.add(link.from_article)
        if link.to_article and link.to_article.pk != article.pk:
            linked_articles.add(link.to_article)

    return linked_articles