from django.core.management import call_command

from plugins.hydra import models, events


def distribute_articles(**kwargs):
    print('We are distributing articles')
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

    # Exclude the current journal
    group_journals.discard(journal)

    results = []

    for journal in group_journals:
        try:
            call_command(
                "copy_articles",
                journal.code,
                article=article.pk,
                target_lang="en",
            )
            results.append(
                {
                    "journal": journal.code,
                    "status": "success",
                }
            )
        except Exception as e:
            print(e)


    return group_journals