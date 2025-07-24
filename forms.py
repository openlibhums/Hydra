from django import forms


from utils import setting_handler, models
from plugins.hydra import plugin_settings


class HydraAdminForm(forms.Form):
    hydra_enable_sidebar = forms.BooleanField(label="Enable Hydra Sidebar", required=False)

    def __init__(self, *args, journal=None, **kwargs):
        """Initialize form with current plugin settings and apply help text."""
        super().__init__(*args, **kwargs)
        self.journal = journal
        self.plugin = models.Plugin.objects.get(
            name=plugin_settings.SHORT_NAME,
        )

        # Initialize fields with settings values and help texts
        hydra_enable_sidebar_setting = setting_handler.get_plugin_setting(
            self.plugin,
            'hydra_enable_sidebar',
            self.journal,
            create=True,
            pretty='Enable Hydra Sidebar',
            types='boolean'
        )
        self.fields[
            'hydra_enable_sidebar'
        ].initial = hydra_enable_sidebar_setting.processed_value

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
