from django.core.management import call_command
from django.db.models import Q, Subquery
from django.utils.translation import get_language_info

from plugins.hydra import models
from submission import models as submission_models
from utils.logger import get_logger


logger = get_logger(__name__)


def get_linked_journals(article):
    journal = article.journal

    # Try direct access via reverse relation
    try:
        linked_group = journal.linked_journals
    except models.LinkedJournals.DoesNotExist:
        try:
            linked_group = models.LinkedJournals.objects.get(links=journal)
        except models.LinkedJournals.DoesNotExist:
            return set()

    # Build set of journals: primary + linked ones
    group_journals = {linked_group.journal}
    group_journals.update(
        link.to_journal for link in
        linked_group.journal_link.select_related("to_journal")
    )

    # Exclude the current journal
    group_journals.discard(journal)

    return group_journals

def distribute_articles(article, journals, stage=None):
    """
    Copies an article into each of the given journals and returns a result
    dict per journal. A failure is logged and doesn't stop the other copies.
    """
    results = []
    for journal in journals:
        try:
            call_command(
                "copy_articles",
                journal.code,
                article=article.pk,
                stage=stage,
            )
            results.append({
                "journal": journal.code,
                "status": "success",
            })
        except Exception as e:
            logger.exception(
                "Hydra: copying article %s to %s failed",
                article.pk,
                journal.code,
            )
            results.append({
                "journal": journal.code,
                "status": "error",
                "message": str(e),
            })
    return results


def journal_language_code(journal):
    """Returns the journal's default language as a Django code, e.g. 'es'."""
    try:
        return journal.get_setting(
            group_name="general",
            setting_name="default_journal_language",
        )
    except Exception:
        return None


def article_language_for(language_code):
    """
    Maps a Django language code (e.g. 'es') to the ISO 639-3 code that
    Article.language uses (e.g. 'spa'), matching on the English name.
    """
    if not language_code:
        return None
    try:
        name = get_language_info(language_code.split("-")[0])["name"]
    except KeyError:
        return None
    for code, label in submission_models.LANGUAGE_CHOICES:
        if str(label).lower() == name.lower():
            return code
    return None

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
