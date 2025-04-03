from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.core.files.base import ContentFile
from django.http import Http404
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from plugins.typesetting import plugin_settings, models, logic, forms, security
from plugins.typesetting.notifications import notify
from security import decorators
from submission import models as submission_models
from core import models as core_models, forms as core_forms, files
from production import logic as production_logic
from journal.views import article_figure
from journal import logic as journal_logic
from utils.logger import get_logger

logger = get_logger(__name__)


@decorators.has_journal
@decorators.editor_user_required
def index(request):
    template = 'hydra/index.html'
    context = {}
    return render(request, template, context)
