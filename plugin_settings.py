from utils import plugins
from utils.install import update_settings
from events import logic as events_logic
from plugins.hydra import events

PLUGIN_NAME = 'Hydra'
DISPLAY_NAME = 'Hydra'
DESCRIPTION = 'A Plugin for multi-journal publishing and linking'
AUTHOR = 'Open Library of Humanities'
VERSION = '0.1'
SHORT_NAME = 'hydra'
MANAGER_URL = 'hydra_index'
JANEWAY_VERSION = '1.7.4'

# Workflow Settings
IS_WORKFLOW_PLUGIN = True
HANDSHAKE_URL = 'hydra_handshake_url'
JUMP_URL = 'hydra_jump_url'
ARTICLE_PK_IN_HANDSHAKE_URL = False
STAGE = 'hydra'
KANBAN_CARD = 'hydra/elements/card.html'


class HydraPlugin(plugins.Plugin):
    plugin_name = PLUGIN_NAME
    display_name = DISPLAY_NAME
    description = DESCRIPTION
    author = AUTHOR
    short_name = SHORT_NAME

    manager_url = MANAGER_URL

    version = VERSION
    janeway_version = JANEWAY_VERSION

    is_workflow_plugin = IS_WORKFLOW_PLUGIN
    handshake_url = HANDSHAKE_URL
    article_pk_in_handshake_url = ARTICLE_PK_IN_HANDSHAKE_URL
    jump_url = JUMP_URL


def install():
    HydraPlugin.install()
    update_settings(file_path="plugins/hydra/install/settings.json")

def register_for_events():
    pass


def hook_registry():
    return {
        'article_sidebar':
            {
                'module': 'plugins.hydra.hooks',
                'function': 'sidebar_article_links',
            },
        'language_header':
            {
                'module': 'plugins.hydra.hooks',
                'function': 'language_header_switcher',
            },
        'journal_editor_nav_block':
            {
                'module': 'plugins.hydra.hooks',
                'function': 'editor_nav_article_switcher',
            }
    }
