from django.contrib import admin
from plugins.hydra import models


@admin.register(models.LinkedArticle)
class ArticleLinkAdmin(admin.ModelAdmin):
    list_display = ("from_article", "to_article")
    search_fields = ("from_article__title", "to_article__title")
    list_filter = ("from_article__journal", "to_article__journal")
    ordering = ("from_article", "to_article")
    raw_id_fields = ("from_article", "to_article")
