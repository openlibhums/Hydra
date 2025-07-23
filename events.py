from plugins.hydra import models

def distribute_articles(**kwargs):
    article = kwargs.get('article')
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

    return group_journals