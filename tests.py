from django.test import TestCase
from django.template import Context
from identifiers.models import Identifier
from utils.testing import helpers

from plugins.hydra import models
from plugins.hydra.hooks import sidebar_article_links


class SidebarArticleLinksTest(TestCase):
    COMMON_PUBID = "test_pub_id"
    def setUp(self):
        helpers.create_press()
        self.journal1, self.journal2 = helpers.create_journals()

        self.linked_journals = models.LinkedJournals.objects.create(journal=self.journal1)
        models.JournalLink.objects.create(
            parent=self.linked_journals,
            to_journal=self.journal2,
            link_type=models.LinkType.TRANSLATION,
        )

        self.article = helpers.create_article(self.journal1)

        self.pubid1 = Identifier.objects.create(
            id_type="pubid",
            identifier=self.COMMON_PUBID,
            article=self.article,
        )

    def test_sidebar_article_links_children(self):
        # Prepare
        request = helpers.Request(journal=self.journal1)
        context = Context({"request": request})
        linked_article = helpers.create_article(self.journal2)

        models.LinkedArticle.objects.create(
            from_article=self.article,
            to_article=linked_article,
        )
        # Expect
        expected = linked_article.url

        # Test
        result = sidebar_article_links(context, self.article)

        self.assertIn(expected, result)

    def test_sidebar_article_links_sibling(self):
        # Prepare
        request = helpers.Request(journal=self.journal1)
        context = Context({"request": request})
        parent_article = helpers.create_article(self.journal2)
        sibling = helpers.create_article(self.journal2)

        models.LinkedArticle.objects.create(
            from_article=parent_article,
            to_article=self.article,
        )

        models.LinkedArticle.objects.create(
            from_article=parent_article,
            to_article=sibling,
        )
        # Expect
        expected = sibling.url

        # Test
        result = sidebar_article_links(context, self.article)

        self.assertIn(expected, result)
