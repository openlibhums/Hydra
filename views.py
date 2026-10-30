from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _

try:
    from plugins.typesetting import plugin_settings, models, logic, security
    from plugins.typesetting.notifications import notify
except ImportError:
    pass
from security import decorators
from utils.logger import get_logger
from plugins.hydra import forms, utils, events, plugin_settings
from submission import models as submission_models
from journal import models as journal_models
from submission.models import Article
from core import models as core_models, views as core_views

from django.http import JsonResponse, HttpResponseNotFound
from django.views.decorators.http import require_POST


logger = get_logger(__name__)


@decorators.has_journal
@decorators.editor_user_required
def index(request):
    form = forms.HydraAdminForm(
        journal=request.journal,
    )
    if request.POST:
        form = forms.HydraAdminForm(
            request.POST,
            journal=request.journal,
        )
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Settings updated successfully',
            )
            return redirect('hydra_index')
    template = 'hydra/index.html'
    context = {
        'form': form,
    }
    return render(request, template, context)


@method_decorator(decorators.has_journal, name="dispatch")
@method_decorator(decorators.editor_user_required, name="dispatch")
class HydraHandshakeView(core_views.GenericFacetedListView):
    """
    Faceted search view for articles in the Hydra plugin.
    Lists only articles from the current journal and in the 'hydra' stage.
    """

    model = submission_models.Article
    template_name = 'hydra/handshake.html'

    def get_facets(self):
        facets = {
            'q': {
                'type': 'search',
                'field_label': _('Search'),
            },
        }
        return self.filter_facets_if_journal(facets)

    def get_order_by_choices(self):
        return [
            ('title', _('Title A–Z')),
            ('-title', _('Title Z–A')),
            ('-date_submitted', _('Newest')),
            ('date_submitted', _('Oldest')),
        ]

    def get_queryset(self, params_querydict=None):
        queryset = super().get_queryset(params_querydict)
        return queryset.filter(
            journal=self.request.journal,
            stage=plugin_settings.STAGE,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hydra_article_search'] = True
        return context


@decorators.editor_user_required
def hydra_jump_url(request, article_id):
    article = get_object_or_404(
        submission_models.Article,
        pk=article_id,
        journal=request.journal,
    )
    linked_journals =  utils.get_linked_journals(
        article,
    )
    if request.POST:
        code_to_distribute = request.POST.get('code_to_distribute')
        if code_to_distribute == 'all':
            journals = linked_journals
        else:
            journal = get_object_or_404(
                journal_models.Journal,
                code=code_to_distribute,
            )
            journals = [journal] if journal in linked_journals else []
            if not journals:
                messages.warning(
                    request,
                    f"Journal with code {code_to_distribute} not linked to this journal",
                )

        results = utils.distribute_articles(
            article,
            journals,
            stage=submission_models.STAGE_EDITOR_COPYEDITING,
        )
        failed = [r["journal"] for r in results if r["status"] == "error"]
        succeeded = [r["journal"] for r in results if r["status"] == "success"]
        if failed:
            messages.error(
                request,
                f"Distribution failed for: {', '.join(failed)}",
            )
        if succeeded:
            # Fetched after distributing so the new copies are included.
            for linked_article in utils.get_interlinked_articles(article.pk):
                element = core_models.WorkflowElement.objects.filter(
                    journal=linked_article.journal,
                    stage=submission_models.STAGE_EDITOR_COPYEDITING,
                ).first()
                if element:
                    core_models.WorkflowLog.objects.get_or_create(
                        article=linked_article,
                        element=element,
                    )
            messages.success(
                request,
                f"Article distributed to: {', '.join(succeeded)}",
            )

        return redirect('hydra_jump_url', article_id=article_id)

    template = 'hydra/jump.html'
    context = {
        'article': article,
        'linked_journals': linked_journals,
        'linked_articles': utils.get_interlinked_articles(article.pk),
    }
    return render(
        request,
        template,
        context,
    )



@staff_member_required
@require_POST
def distribute_articles_view(request, article_id):
    try:
        article = Article.objects.get(pk=article_id)
    except Article.DoesNotExist:
        return HttpResponseNotFound("Article not found")

    results = events.distribute_articles(
        article=article,
    )

    if not results:
        return JsonResponse({"status": "No linked journals found"}, status=200)

    return JsonResponse({
        "article_id": article.pk,
        "source_journal": article.journal.code,
        "results": results,
    })
