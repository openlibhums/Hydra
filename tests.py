from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase
from django.template import Context
from identifiers.models import Identifier
from utils import setting_handler
from utils.install import update_settings
from utils.testing import helpers

from plugins.hydra import events, hooks, models, utils, views
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


class LinkedJournalsTestCase(TestCase):
    """Two journals in one Hydra group, with an article in the first."""

    def setUp(self):
        helpers.create_press()
        self.journal1, self.journal2 = helpers.create_journals()
        self.linked_journals = models.LinkedJournals.objects.create(
            journal=self.journal1,
        )
        models.JournalLink.objects.create(
            parent=self.linked_journals,
            to_journal=self.journal2,
            link_type=models.LinkType.TRANSLATION,
        )
        self.article = helpers.create_article(self.journal1)
        self.factory = RequestFactory()

class GetInterlinkedArticlesTest(LinkedJournalsTestCase):
    def test_interlinked_articles_see_new_links(self):
        self.assertEqual(utils.get_interlinked_articles(self.article.pk), set())
        copy = helpers.create_article(self.journal2)
        models.LinkedArticle.objects.create(
            from_article=self.article,
            to_article=copy,
        )
        self.assertEqual(utils.get_interlinked_articles(self.article.pk), {copy})

class DistributeArticlesTest(LinkedJournalsTestCase):
    def test_events_distribute_copies_once_per_linked_journal(self):
        with mock.patch("plugins.hydra.utils.call_command") as call:
            results = events.distribute_articles(article=self.article)
        call.assert_called_once_with(
            "copy_articles",
            self.journal2.code,
            article=self.article.pk,
            stage=None,
        )
        self.assertEqual(
            results,
            [{"journal": self.journal2.code, "status": "success"}],
        )

    def test_distribute_logs_and_reports_failures(self):
        with mock.patch(
            "plugins.hydra.utils.call_command",
            side_effect=Exception("boom"),
        ), mock.patch("plugins.hydra.utils.logger") as logger:
            results = utils.distribute_articles(self.article, [self.journal2])
        logger.exception.assert_called_once()
        self.assertEqual(results[0]["status"], "error")

class HydraViewsTest(LinkedJournalsTestCase):
    def test_distribute_view_rejects_get(self):
        request = self.factory.get("/")
        request.user = helpers.create_user(
            "staff@example.org",
            is_staff=True,
            is_active=True,
        )
        response = views.distribute_articles_view(request, self.article.pk)
        self.assertEqual(response.status_code, 405)

    def test_handshake_view_is_not_public(self):
        request = self.factory.get("/")
        request.journal = self.journal1
        request.user = AnonymousUser()
        try:
            response = views.HydraHandshakeView.as_view()(request)
        except PermissionDenied:
            return
        self.assertNotEqual(response.status_code, 200)

class LanguageHeaderSwitcherTest(LinkedJournalsTestCase):
    def setUp(self):
        super().setUp()
        update_settings(file_path="plugins/hydra/install/settings.json")

    def test_language_switcher_skips_submission_journals(self):
        copy = helpers.create_article(self.journal2)
        models.LinkedArticle.objects.create(
            from_article=self.article,
            to_article=copy,
        )
        request = self.factory.get("/")
        request.journal = self.journal1
        context = {"request": request, "article": self.article}

        self.assertIn(
            self.journal2.site_url(path="/"),
            hooks.language_header_switcher(context),
        )
        setting_handler.save_setting(
            "plugin:hydra",
            "hydra_submission_journal",
            self.journal2,
            "On",
        )
        self.assertEqual(hooks.language_header_switcher(context), "")
