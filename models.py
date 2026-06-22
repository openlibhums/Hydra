from django.db import models
from django.utils.translation import gettext_lazy as _

from core.model_utils import DynamicChoiceField

class LinkType(models.TextChoices):
    TRANSLATION = "translation", _("Translation")
    #
    # The following link types / relations are *editorially significant* changes described in
    # https://data.crossref.org/reports/help/schema_doc/5.4.0/schema_5_4_0.html#update
    ADDENDUM = "addendum", _("Addendum")
    CLARIFICATION = "clarification", _("Clarification")
    CORRECTION = "correction", _("Correction")
    CORRIGENDUM = "corrigendum", _("Corrigendum")
    ERRATUM = "erratum", _("Erratum")
    EXPRESSION_OF_CONCERN = "expression_of_concern", _("Expression of concern")
    NEW_EDITION = "new_edition", _("New edition")
    NEW_VERSION = "new_version", _("New version")
    PARTIAL_RETRACTION = "partial_retraction", _("Partial retraction")
    REMOVAL = "removal", _("Removal")
    RETRACTION = "retraction", _("Retraction")
    WITHDRAWAL = "withdrawal", _("Withdrawal")

class JournalLink(models.Model):


    parent = models.ForeignKey(
        "hydra.LinkedJournals",
        on_delete=models.CASCADE,
        related_name="journal_link",
    )
    to_journal = models.ForeignKey(
        "journal.Journal",
        on_delete=models.CASCADE,
        related_name="link_to"
    )

    link_type = DynamicChoiceField(
        max_length=255,
        choices=LinkType.choices,
        default=LinkType.TRANSLATION
    )

    class Meta:
        unique_together = ("parent", "to_journal", "link_type")

    def __str__(self):
        return f"{self.parent.journal} -> {self.to_journal} ({self.link_type})"


class LinkedJournals(models.Model):
    journal = models.OneToOneField(
        "journal.Journal",
        on_delete=models.CASCADE,
        related_name="linked_journals",
    )
    links = models.ManyToManyField(
        "journal.Journal",
        through="hydra.JournalLink",
        related_name="linked_to",
        blank=True,
    )

    def __str__(self):
        return f"Links of {self.journal}"


class LinkedArticle(models.Model):
    from_article = models.ForeignKey(
        "submission.Article",
        on_delete=models.CASCADE,
        related_name="linked_from",
        help_text="The original or initial paper",
    )
    to_article = models.ForeignKey(
        "submission.Article",
        on_delete=models.CASCADE,
        related_name="linked_to",
        help_text="The related paper",
    )
    relationship = DynamicChoiceField(
        max_length=256,
        choices=LinkType.choices,
        default=LinkType.TRANSLATION,
        help_text="The relationship; to be read as 'to-article' is a 'relationship' of 'from-article'"
    )

    class Meta:
        unique_together = ("from_article", "to_article", "relationship")

    def __str__(self):
        return f"{self.from_article.pk} -> {self.to_article.pk} ({self.relationship})"
