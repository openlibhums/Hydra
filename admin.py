from django.contrib import admin
from plugins.hydra import models


@admin.register(models.LinkedArticle)
class ArticleLinkAdmin(admin.ModelAdmin):
    list_display = ("from_article", "to_article")
    search_fields = ("from_article__title", "to_article__title")
    list_filter = ("from_article__journal", "to_article__journal")
    ordering = ("from_article", "to_article")
    raw_id_fields = ("from_article", "to_article")


@admin.register(models.JournalLink)
class JournalLinkAdmin(admin.ModelAdmin):
    list_display = ("parent", "to_journal", "link_type")
    search_fields = (
        "parent__journal__title",
        "to_journal__title",
    )
    list_filter = ("link_type", "parent__journal")
    raw_id_fields = ("parent", "to_journal")
    ordering = ("parent", "to_journal")


@admin.register(models.LinkedJournals)
class LinkedJournalsAdmin(admin.ModelAdmin):
    list_display = ("journal",)
    search_fields = ("journal__title",)
    raw_id_fields = ("journal",)