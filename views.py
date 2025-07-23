from django.shortcuts import render, redirect
from django.contrib import messages

try:
    from plugins.typesetting import plugin_settings, models, logic, security
    from plugins.typesetting.notifications import notify
except ImportError:
    pass
from security import decorators
from utils.logger import get_logger
from plugins.hydra import forms

logger = get_logger(__name__)


@decorators.has_journal
@decorators.editor_user_required
def index(request):
    form = forms.HydraAdminForm(
        journal=request.journal,
    )
    if request.POST:
        print(request.POST)
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
