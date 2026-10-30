from django import forms


from utils import setting_handler, models
from plugins.hydra import plugin_settings


class HydraAdminForm(forms.Form):
    hydra_enable_sidebar = forms.BooleanField(
        label="Enable Hydra Sidebar",
        required=False,
    )
    hydra_submission_journal = forms.BooleanField(
        label="Submission journal",
        help_text=(
            "Articles are submitted to this journal and distributed from it, "
            "so it is left out of the language switcher."
        ),
        required=False,
    )

    def __init__(self, *args, journal=None, **kwargs):
        """Initialize form with current plugin settings and apply help text."""
        super().__init__(*args, **kwargs)
        self.journal = journal
        self.plugin = models.Plugin.objects.get(
            name=plugin_settings.SHORT_NAME,
        )

        # Initialize fields with settings values
        for setting_name, field in self.fields.items():
            setting = setting_handler.get_plugin_setting(
                self.plugin,
                setting_name,
                self.journal,
                create=True,
                pretty=field.label,
                types='boolean'
            )
            field.initial = setting.processed_value

    def save(self):
        """Save each setting in the cleaned data to the plugin settings."""
        for setting_name, setting_value in self.cleaned_data.items():
            if setting_value:
                setting_value = 'On'
            else:
                setting_value = ''
            setting_handler.save_plugin_setting(
                plugin=self.plugin,
                setting_name=setting_name,
                value=setting_value,
                journal=self.journal
            )
