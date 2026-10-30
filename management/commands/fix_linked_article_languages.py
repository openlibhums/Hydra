from django.core.management.base import BaseCommand
from django.db import transaction

from submission import models as submission_models
from plugins.hydra import models
from plugins.hydra import utils as hydra_utils


class Command(BaseCommand):
    """
    Sets the language of linked articles from their journal's default
    language, and their English title from the matching translated title,
    as copy_articles now does for new copies. Dry run unless --commit.
    """

    help = (
        "Corrects the language and title of linked articles from their "
        "journal's default language."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--journal',
            action='append',
            dest='journal_codes',
            help='Only fix articles in this journal. Can be repeated.',
        )
        parser.add_argument(
            '--commit',
            action='store_true',
            help='Save the changes. Without this nothing is written.',
        )

    def handle(self, *args, **options):
        links = models.LinkedArticle.objects.all()
        article_ids = set(links.values_list('from_article', flat=True))
        article_ids |= set(links.values_list('to_article', flat=True))
        articles = submission_models.Article.objects.filter(
            pk__in=article_ids,
        ).select_related('journal').order_by('journal__code', 'pk')
        if options['journal_codes']:
            articles = articles.filter(journal__code__in=options['journal_codes'])

        changed = 0
        with transaction.atomic():
            for article in articles:
                changes = self.changes_for(article)
                if not changes:
                    continue
                changed += 1
                self.stdout.write('{} [{}]: {}'.format(
                    article.journal.code,
                    article.pk,
                    '; '.join(
                        '{} {!r} -> {!r}'.format(field, old, new)
                        for field, (old, new) in changes.items()
                    ),
                ))
                if options['commit']:
                    for field, (_, new) in changes.items():
                        setattr(article, field, new)
                    article.save()

        if options['commit']:
            self.stdout.write(self.style.SUCCESS(
                'Updated {} article(s).'.format(changed),
            ))
        else:
            self.stdout.write(self.style.WARNING(
                '{} article(s) would change. Dry run: nothing saved. '
                'Use --commit.'.format(changed),
            ))

    def changes_for(self, article):
        language_code = hydra_utils.journal_language_code(article.journal)
        if not language_code:
            return {}

        changes = {}
        article_language = hydra_utils.article_language_for(language_code)
        if article_language and article.language != article_language:
            changes['language'] = (article.language, article_language)

        if not language_code.startswith('en'):
            translated_title = getattr(article, 'title_{}'.format(language_code), None)
            if translated_title and translated_title != article.title_en:
                changes['title_en'] = (article.title_en, translated_title)
                changes['title'] = (article.title, translated_title)

        return changes
