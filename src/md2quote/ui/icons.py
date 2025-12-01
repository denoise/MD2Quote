"""
Material Symbols icon support for MD2Quote.

Uses Google's Material Symbols Outlined font for modern, monochrome icons.
The font supports variable weight, optical size, grade, and fill.
"""

import os
from pathlib import Path
from PyQt6.QtGui import QFont, QFontDatabase, QIcon, QPainter, QPixmap, QColor
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtWidgets import QApplication

# Material Symbols codepoints (Unicode)
ICONS = {
    'folder_open': '\ue2c8',
    'save': '\ue161',
    'file_save': '\uf17f',
    'download': '\uf090',
    'upload': '\uf09b',
    'file_copy': '\ue173',
    'description': '\ue873',
    
    'picture_as_pdf': '\ue415',
    'print': '\ue8ad',
    'share': '\ue80d',
    'ios_share': '\ue6b8',
    
    'settings': '\ue8b8',
    'tune': '\ue429',
    'build': '\ue869',
    'handyman': '\uf10b',
    
    'arrow_back': '\ue5c4',
    'arrow_forward': '\ue5c8',
    'close': '\ue5cd',
    'menu': '\ue5d2',
    'more_vert': '\ue5d4',
    'more_horiz': '\ue5d3',
    'expand_more': '\ue5cf',
    'expand_less': '\ue5ce',
    'chevron_left': '\ue5cb',
    'chevron_right': '\ue5cc',
    
    'add': '\ue145',
    'remove': '\ue15b',
    'edit': '\ue3c9',
    'delete': '\ue872',
    'refresh': '\ue5d5',
    'search': '\ue8b6',
    'check': '\ue5ca',
    'done': '\ue876',
    'done_all': '\ue877',
    'undo': '\ue166',
    'redo': '\ue15a',
    
    'content_copy': '\ue14d',
    'content_paste': '\ue14f',
    'content_cut': '\ue14e',
    'select_all': '\ue162',
    
    'visibility': '\ue8f4',
    'visibility_off': '\ue8f5',
    'fullscreen': '\ue5d0',
    'fullscreen_exit': '\ue5d1',
    'zoom_in': '\ue8ff',
    'zoom_out': '\ue900',
    
    'info': '\ue88e',
    'warning': '\ue002',
    'error': '\ue000',
    'help': '\ue887',
    'check_circle': '\ue86c',
    'cancel': '\ue5c9',
    
    'badge': '\uea67',
    'person': '\ue7fd',
    'business': '\ue0af',
    'contact_page': '\uf22e',
    'article': '\uef42',
    'text_snippet': '\uf1c6',
    'palette': '\ue40a',
    'brush': '\ue3ae',
    'format_paint': '\ue243',
    'format_size': '\ue245',
    'text_format': '\ue165',
    'color_lens': '\ue3b7',
    'settings_applications': '\ue8b9',
    'admin_panel_settings': '\uef3d',
    'manage_accounts': '\uf02e',
    
    'receipt_long': '\uef6e',
    'request_quote': '\uf1b6',
    'payments': '\uef63',
    'account_balance': '\ue84f',
    'calculate': '\uea5f',
    'summarize': '\uf071',
    
    'dashboard': '\ue871',
    'view_agenda': '\ue8e9',
    'table_chart': '\ue265',
    'grid_view': '\ue9b0',
    'list': '\ue896',
    'view_module': '\ue8f3',
    
    'format_bold': '\ue238',
    'format_italic': '\ue23f',
    'format_underlined': '\ue249',
    'format_list_bulleted': '\ue241',
    'format_list_numbered': '\ue242',
    'format_quote': '\ue244',
    'code': '\ue86f',
    'title': '\ue264',
    
    'schedule': '\ue8b5',
    'calendar_today': '\ue935',
    'event': '\ue878',
    'attach_money': '\ue227',
    'euro': '\uea15',
    'language': '\ue894',
    'translate': '\ue8e2',
    'tag': '\ue867',
    'label': '\ue892',
    'bookmark': '\ue866',
    'star': '\ue838',
    'favorite': '\ue87d',
    'send': '\ue163',
    'smart_toy': '\uf06c',
    'add_circle': '\ue147',
    
    'branding_watermark': '\ue06b',
    'image': '\ue3f4',
    'photo_library': '\ue413',
    
    'pin': '\uf045',
    'numbers': '\ueac7',
    'counter_1': '\ue0fb',
    'counter_2': '\ue0fc',
    'counter_3': '\ue0fd',
    'counter_4': '\ue0fe',
    'counter_5': '\ue0ff',

    'auto_awesome': '\ue65f',
}


class MaterialIcons:
    """Material Symbols icon provider for PyQt6."""
    
    _instance = None
    _font_loaded = False
    _font_family = "Material Symbols Outlined"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not MaterialIcons._font_loaded:
            self._load_font()
    
    def _load_font(self):
        """Load the Material Symbols font from assets."""
        from md2quote.utils import get_assets_path
        
        font_file = get_assets_path() / "fonts" / "MaterialSymbolsOutlined.ttf"
        
        if font_file.exists():
            font_id = QFontDatabase.addApplicationFont(str(font_file))
            if font_id >= 0:
                families = QFontDatabase.applicationFontFamilies(font_id)
                if families:
                    MaterialIcons._font_family = families[0]
                MaterialIcons._font_loaded = True
            else:
                print(f"Warning: Failed to load Material Symbols font from {font_file}")
        else:
            print(f"Warning: Material Symbols font file not found at {font_file}")
    
    def get_font(self, size: int = 20) -> QFont:
        """Get a QFont configured for Material Symbols."""
        font = QFont(MaterialIcons._font_family)
        font.setPixelSize(size)
        font.setWeight(QFont.Weight.Normal)
        return font
    
    def get_char(self, name: str) -> str:
        """Get the Unicode character for an icon name."""
        return ICONS.get(name, '\ue88e')
    
    def get_icon(self, name: str, size: int = 24, color: str = None) -> QIcon:
        """
        Generate a QIcon from a Material Symbol.
        
        Args:
            name: Icon name from ICONS dict
            size: Pixel size for the icon
            color: Hex color string (e.g., '#ffffff'). If None, uses current palette.
        """
        char = self.get_char(name)
        
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        font = self.get_font(size)
        painter.setFont(font)
        
        if color:
            painter.setPen(QColor(color))
        else:
            app = QApplication.instance()
            if app:
                painter.setPen(app.palette().text().color())
        
        painter.drawText(QRect(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, char)
        painter.end()
        
        return QIcon(pixmap)


# Singleton instance
_icons = None


def get_icons() -> MaterialIcons:
    """Get the MaterialIcons singleton instance."""
    global _icons
    if _icons is None:
        _icons = MaterialIcons()
    return _icons


def icon(name: str, size: int = 20, color: str = None) -> QIcon:
    """
    Convenience function to get a Material Symbol icon.
    
    Args:
        name: Icon name (e.g., 'settings', 'save', 'folder_open')
        size: Icon size in pixels
        color: Optional hex color string
    
    Returns:
        QIcon with the rendered symbol
    """
    return get_icons().get_icon(name, size, color)


def icon_char(name: str) -> str:
    """
    Get just the Unicode character for an icon.
    Useful for inserting into labels with the Material Symbols font applied.
    """
    return get_icons().get_char(name)


def icon_font(size: int = 20) -> QFont:
    """Get a QFont configured for Material Symbols at the given size."""
    return get_icons().get_font(size)


