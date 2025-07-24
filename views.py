from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.core.management import call_command

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
from core import models as core_models

from django.http import JsonResponse, HttpResponseNotFound
from django.views.decorators.http import require_GET


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


@decorators.editor_user_required
def hydra_handshake_url(request):
    articles_in_stage = submission_models.Article.objects.filter(
        stage=plugin_settings.STAGE,
    )
    template = 'hydra/handshake.html'
    context = {
        'articles_in_stage': articles_in_stage,
    }
    return render(
        request,
        template,
        context,
    )


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
    linked_articles = utils.get_interlinked_articles(article.pk)
    error = None
    if request.POST:
        code_to_distribute = request.POST.get('code_to_distribute')
        if code_to_distribute == 'all':
            error = utils.distribute_articles(article, linked_journals)
        else:
            journal = get_object_or_404(
                journal_models.Journal,
                code=code_to_distribute,
            )
            if journal in linked_journals:
                error = utils.distribute_articles(article, [journal])
            else:
                messages.warning(
                    request,
                    f"Journal with code {code_to_distribute} not linked to this journal",
                )
        if error:
            messages.error(
                request,
                error,
            )
        else:
            stage = submission_models.STAGE_EDITOR_COPYEDITING
            element = core_models.WorkflowElement.objects.get(
                journal=article.journal,
                stage=stage,
            )
            for linked_article in linked_articles:
                core_models.WorkflowLog.objects.get_or_create(
                    article=linked_article,
                    element=element,
                )
            messages.success(
                request,
                "Articles distributed successfully",
            )

        return redirect('hydra_jump_url', article_id=article_id)

    template = 'hydra/jump.html'
    context = {
        'article': article,
        'linked_journals': linked_journals,
        'linked_articles': linked_articles,
    }
    return render(
        request,
        template,
        context,
    )



@staff_member_required
@require_GET
def distribute_articles_view(request, article_id):
    try:
        article = Article.objects.get(pk=article_id)
    except Article.DoesNotExist:
        return HttpResponseNotFound("Article not found")

    journals = events.distribute_articles(
        article=article,
    )

    if not journals:
        return JsonResponse({"status": "No linked journals found"}, status=200)

    results = []

    for journal in journals:
        try:
            call_command(
                "copy_articles",
                article.journal.code,
                journal_code=journal.code,
                article=article.pk,
                target_lang='en',
            )
            results.append({
                "journal": journal.code,
                "status": "success",
            })
        except Exception as e:
            results.append({
                "journal": journal.code,
                "status": "error",
                "message": str(e),
            })

    return JsonResponse({
        "article_id": article.pk,
        "source_journal": article.journal.code,
        "results": results,
    })