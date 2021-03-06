from PyQt5 import uic
from PyQt5.QtWidgets import QCheckBox

from vorta.i18n import translate
from vorta.utils import get_asset
from vorta.autostart import open_app_at_startup
from vorta.models import SettingsModel, BackupProfileMixin, get_misc_settings
from vorta._version import __version__
from vorta.views.utils import get_theme_class
from vorta.config import LOG_DIR

uifile = get_asset('UI/misctab.ui')
MiscTabUI, MiscTabBase = uic.loadUiType(uifile, from_imports=True, import_from=get_theme_class())


class MiscTab(MiscTabBase, MiscTabUI, BackupProfileMixin):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(parent)
        self.versionLabel.setText(__version__)
        self.logLink.setText(f"<a href='file://{LOG_DIR}'>Log</a>")

        for setting in SettingsModel.select().where(SettingsModel.type == 'checkbox'):
            x = filter(lambda s: s['key'] == setting.key, get_misc_settings())
            if not list(x):  # Skip settings that aren't specified in vorta.models.
                continue
            b = QCheckBox(translate('settings', setting.label))
            b.setCheckState(setting.value)
            b.setTristate(False)
            b.stateChanged.connect(lambda v, key=setting.key: self.save_setting(key, v))
            self.checkboxLayout.addWidget(b)

    def save_setting(self, key, new_value):
        setting = SettingsModel.get(key=key)
        setting.value = bool(new_value)
        setting.save()

        if key == 'autostart':
            open_app_at_startup(new_value)

    def set_borg_details(self, borg_details):
        self.borgVersion.setText(borg_details['version'])
        self.borgPath.setText(borg_details['path'])
