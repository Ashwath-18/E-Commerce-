"""
Generates gui/styles/light.qss and gui/styles/dark.qss from one
token-driven template (colors come from gui/styles/colors.py).

Run from anywhere:   python gui/styles/build_qss.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from gui.styles import colors  # noqa: E402


def shade(hex_color, factor):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (max(0, min(255, int(c * factor))) for c in (r, g, b))
    return f"#{r:02X}{g:02X}{b:02X}"


def lg(a, b, horizontal=False, vertical=False, mid=None):
    if horizontal:
        coords = "x1:0, y1:0, x2:1, y2:0"
    elif vertical:
        coords = "x1:0, y1:0, x2:0, y2:1"
    else:
        coords = "x1:0, y1:0, x2:1, y2:1"
    stops = f"stop:0 {a}, stop:1 {b}"
    if mid:
        stops = f"stop:0 {a}, stop:0.55 {mid}, stop:1 {b}"
    return f"qlineargradient({coords}, {stops})"


TEMPLATE = r"""
/* ===================================================================
   Cartify - $THEME_NAME theme
   Generated from one token-driven template so both themes share the
   exact same structure. Colours are tuned per theme.
   =================================================================== */

/* ---------------- Base ---------------- */

QWidget {
    color: $TEXT;
    font-family: "Segoe UI", "Inter", "Helvetica Neue", Arial;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: $BACKGROUND;
}

QLabel {
    background: transparent;
}

QStackedWidget {
    background: transparent;
}

QScrollArea {
    background: transparent;
    border: none;
}

QScrollArea > QWidget > QWidget {
    background: transparent;
}

QScrollArea > QWidget#qt_scrollarea_viewport {
    background: transparent;
}

QToolTip {
    background-color: $TOOLTIP_BG;
    color: $TOOLTIP_TEXT;
    border: 1px solid $TOOLTIP_BORDER;
    padding: 6px 10px;
    border-radius: 8px;
}

/* ---------------- Canvas + Shell ---------------- */

#Canvas {
    background: $G_CANVAS;
}

#Shell {
    background-color: $SHELL;
    border: 1px solid $SHELL_BORDER;
    border-radius: 32px;
}

/* ---------------- Sidebar (floating violet pill) ---------------- */

#Sidebar {
    background: $G_SIDEBAR;
    border: 1px solid $SIDEBAR_BORDER;
    border-radius: 30px;
}

#SidebarScroll {
    background: transparent;
    border: none;
}

#SidebarNav {
    background: transparent;
}

#SidebarTitle {
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 800;
}

#SidebarCaption {
    color: rgba(255, 255, 255, 165);
    font-size: 11px;
}

#SidebarDivider {
    background-color: rgba(255, 255, 255, 38);
    max-height: 1px;
    border: none;
}

QPushButton#NavButton {
    background-color: transparent;
    color: rgba(255, 255, 255, 195);
    text-align: left;
    padding-left: 16px;
    border: 1px solid transparent;
    border-radius: 17px;
    font-size: 14px;
    font-weight: 600;
}

QPushButton#NavButton:hover {
    background-color: rgba(255, 255, 255, 32);
    color: #FFFFFF;
}

QPushButton#NavButton:checked {
    background-color: rgba(255, 255, 255, 58);
    border: 1px solid rgba(255, 255, 255, 80);
    color: #FFFFFF;
    font-weight: 700;
}

QPushButton#NavButton:pressed {
    background-color: rgba(255, 255, 255, 76);
}

QPushButton#NavButton[collapsed="true"] {
    padding-left: 0px;
    text-align: center;
}

/* ---------------- Header ---------------- */

#Navbar {
    background: transparent;
}

#NavbarCrumb {
    color: $TEXT_LIGHT;
    font-size: 14px;
    font-weight: 600;
}

#NavbarTitle {
    color: $TEXT;
    font-size: 15px;
    font-weight: 800;
}

#NavbarSubtitle {
    color: $TEXT_LIGHT;
    font-size: 13px;
}

#NavbarUserChip {
    background-color: $CARD;
    border: 1px solid $CARD_BORDER;
    border-radius: 25px;
}

#NavbarAdmin {
    color: $TEXT;
    font-size: 13px;
    font-weight: 700;
}

#NavbarRole {
    color: $TEXT_LIGHT;
    font-size: 11px;
}

#AdminAvatar {
    background: $G_VIOLET;
    color: #FFFFFF;
    border-radius: 18px;
    font-weight: 800;
    font-size: 14px;
}

QToolButton#ThemeToggle {
    background-color: $CARD;
    border: 1px solid $CARD_BORDER;
    border-radius: 22px;
    padding: 0px;
}

QToolButton#ThemeToggle:hover {
    background-color: $SOFT;
    border: 1px solid $SOFT_BORDER;
}

/* ---------------- Cards ---------------- */

#Card, #ChartCard, #StatCard, #FilterBar {
    background-color: $CARD;
    border: 1px solid $CARD_BORDER;
    border-radius: 24px;
}

#FilterBar {
    border-radius: 22px;
}

#StatCard[clickable="true"]:hover {
    border: 1px solid $CARD_BORDER_HOVER;
    background-color: $CARD_HOVER;
}

#HeroCard {
    background: $G_HERO;
    border: 1px solid $HERO_BORDER;
    border-radius: 30px;
}

#AccentCardViolet {
    background: $G_VIOLET_SOFT;
    border: 1px solid $HERO_BORDER;
    border-radius: 28px;
}

#AccentCardPink {
    background: $G_PINK;
    border: 1px solid $HERO_BORDER_PINK;
    border-radius: 28px;
}

#AccentCardViolet[clickable="true"]:hover, #AccentCardPink[clickable="true"]:hover {
    border: 1px solid rgba(255, 255, 255, 150);
}

#HeroTitle {
    color: #FFFFFF;
    font-size: 17px;
    font-weight: 700;
}

#HeroSub {
    color: rgba(255, 255, 255, 175);
    font-size: 12px;
}

#HeroGlass {
    background-color: rgba(255, 255, 255, 30);
    border: 1px solid rgba(255, 255, 255, 46);
    border-radius: 22px;
}

#HeroGlassStrong {
    background-color: rgba(255, 255, 255, 56);
    border: 1px solid rgba(255, 255, 255, 84);
    border-radius: 22px;
}

#HeroKpiValue {
    color: #FFFFFF;
    font-size: 24px;
    font-weight: 800;
}

#HeroKpiLabel {
    color: rgba(255, 255, 255, 185);
    font-size: 11px;
    font-weight: 600;
}

#AccentTitle {
    color: #FFFFFF;
    font-size: 16px;
    font-weight: 700;
}

#AccentSub {
    color: rgba(255, 255, 255, 195);
    font-size: 12px;
}

#AccentValue {
    color: #FFFFFF;
    font-size: 32px;
    font-weight: 800;
}

QPushButton#GlassButton {
    background-color: rgba(255, 255, 255, 52);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 84);
    border-radius: 17px;
    min-width: 34px;
    max-width: 34px;
    min-height: 34px;
    max-height: 34px;
    padding: 0px;
}

QPushButton#GlassButton:hover {
    background-color: rgba(255, 255, 255, 82);
}

#StatValue {
    color: $TEXT;
    font-size: 29px;
    font-weight: 800;
}

#StatTitle {
    color: $TEXT_LIGHT;
    font-size: 13px;
    font-weight: 600;
}

#StatCaption {
    color: $TEXT_LIGHT;
    font-size: 11px;
}

#StatShare {
    color: $SUCCESS;
    font-size: 11px;
    font-weight: 700;
}

#StatLink {
    color: $SOFT_TEXT;
    background-color: $SOFT;
    border: 1px solid $SOFT_BORDER;
    border-radius: 12px;
    padding: 3px 11px;
    font-size: 11px;
    font-weight: 700;
}

#TileValue {
    color: $TEXT;
    font-size: 25px;
    font-weight: 800;
}

#ChartTitle {
    color: $TEXT;
    font-size: 16px;
    font-weight: 800;
}

#ChartSub {
    color: $TEXT_LIGHT;
    font-size: 12px;
}

#PanelLabel {
    color: $TEXT_LIGHT;
    font-size: 12px;
    font-weight: 600;
}

#PanelValue {
    color: $TEXT;
    font-size: 13px;
    font-weight: 800;
}

#MetricTile {
    background-color: $SURFACE_ALT;
    border: 1px solid $CARD_BORDER;
    border-radius: 18px;
}

#DetailText {
    color: $TEXT;
    background-color: transparent;
}

#DetailSection {
    color: $TEXT;
    font-size: 15px;
    font-weight: 800;
}

#DetailValue {
    color: $TEXT;
    font-size: 14px;
    font-weight: 700;
}

#SettingsDivider {
    background-color: $ROW_LINE;
    border: none;
}

#SettingsRow {
    background-color: transparent;
}

#SettingsItemTitle {
    color: $TEXT;
    font-size: 14px;
    font-weight: 700;
}

#SettingsItemDescription {
    color: $TEXT_LIGHT;
    font-size: 12px;
}

/* ---------------- Pills / badges ---------------- */

QLabel#Pill, QLabel#SettingsValuePill {
    background-color: $SOFT;
    color: $SOFT_TEXT;
    border: 1px solid $SOFT_BORDER;
    border-radius: 13px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 700;
}

QLabel#Pill[tone="pink"] {
    background-color: $PILL_PINK_BG;
    color: $PILL_PINK_TEXT;
    border: 1px solid $PILL_PINK_BORDER;
}

QLabel#Pill[tone="green"] {
    background-color: $PILL_GREEN_BG;
    color: $PILL_GREEN_TEXT;
    border: 1px solid $PILL_GREEN_BORDER;
}

QLabel#Pill[tone="amber"] {
    background-color: $PILL_AMBER_BG;
    color: $PILL_AMBER_TEXT;
    border: 1px solid $PILL_AMBER_BORDER;
}

/* ---------------- Buttons ---------------- */

QPushButton#PrimaryButton {
    background: $G_VIOLET_H;
    color: #FFFFFF;
    border: 1px solid $PRIMARY_BTN_BORDER;
    border-radius: 16px;
    padding: 10px 22px;
    font-weight: 700;
    font-size: 13px;
}

QPushButton#PrimaryButton:hover {
    background: $G_VIOLET_H_HOVER;
}

QPushButton#PrimaryButton:pressed {
    background: $G_VIOLET_H_PRESSED;
    padding-top: 11px;
    padding-bottom: 9px;
}

QPushButton#PrimaryButton:disabled {
    background: $TRACK;
    color: $TEXT_LIGHT;
    border: 1px solid $TRACK;
}

QPushButton#SecondaryButton {
    background-color: $CARD;
    color: $TEXT;
    border: 1px solid $INPUT_BORDER;
    border-radius: 16px;
    padding: 10px 20px;
    font-weight: 700;
    font-size: 13px;
}

QPushButton#SecondaryButton:hover {
    background-color: $SOFT;
    border: 1px solid $SOFT_BORDER;
    color: $SOFT_TEXT;
}

QPushButton#SecondaryButton:pressed {
    background-color: $SOFT_BORDER;
    padding-top: 11px;
    padding-bottom: 9px;
}

QPushButton#SecondaryButton:disabled {
    background-color: $SURFACE_ALT;
    color: $TEXT_LIGHT;
    border: 1px solid $ROW_LINE;
}

QPushButton#DangerButton {
    background: $G_DANGER_H;
    color: #FFFFFF;
    border: 1px solid $DANGER_BTN_BORDER;
    border-radius: 16px;
    padding: 10px 20px;
    font-weight: 700;
    font-size: 13px;
}

QPushButton#DangerButton:hover {
    background: $G_DANGER_H_HOVER;
}

QPushButton#DangerButton:pressed {
    background: $G_DANGER_H_PRESSED;
    padding-top: 11px;
    padding-bottom: 9px;
}

QPushButton#SendButton {
    background: $G_VIOLET;
    border: 1px solid $PRIMARY_BTN_BORDER;
    border-radius: 22px;
    min-width: 44px;
    max-width: 44px;
    min-height: 44px;
    max-height: 44px;
    padding: 0px;
}

QPushButton#SendButton:hover {
    background: $G_VIOLET_HOVER;
}

QPushButton#SendButton:disabled {
    background: $TRACK;
    border: 1px solid $TRACK;
}

QToolButton#SortButton, QToolButton#IconButton {
    background-color: $CARD;
    border: 1px solid $INPUT_BORDER;
    border-radius: 16px;
    padding: 7px;
}

QToolButton#SortButton:hover, QToolButton#IconButton:hover {
    background-color: $SOFT;
    border: 1px solid $SOFT_BORDER;
}

QToolButton#SortButton:pressed, QToolButton#IconButton:pressed {
    background-color: $SOFT_BORDER;
}

QToolButton#SortButton::menu-indicator {
    image: none;
    width: 0px;
}

QMenu {
    background-color: $CARD;
    border: 1px solid $CARD_BORDER_HOVER;
    border-radius: 14px;
    padding: 7px;
}

QMenu::item {
    padding: 9px 30px 9px 14px;
    border-radius: 9px;
    color: $TEXT;
}

QMenu::item:selected {
    background-color: $SOFT;
    color: $SOFT_TEXT;
}

QMenu::separator {
    height: 1px;
    background: $ROW_LINE;
    margin: 6px 8px;
}

/* ---------------- Inputs ---------------- */

QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox, QTextEdit {
    background-color: $INPUT_BG;
    border: 1px solid $INPUT_BORDER;
    border-radius: 15px;
    padding: 9px 14px;
    color: $TEXT;
    selection-background-color: $PRIMARY;
    selection-color: #FFFFFF;
}

QLineEdit:hover, QComboBox:hover, QDateEdit:hover, QDoubleSpinBox:hover, QSpinBox:hover, QTextEdit:hover {
    border: 1px solid $INPUT_BORDER_HOVER;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QTextEdit:focus {
    border: 1px solid $PRIMARY;
    background-color: $INPUT_FOCUS_BG;
}

QLineEdit:disabled, QComboBox:disabled, QDateEdit:disabled, QDoubleSpinBox:disabled, QSpinBox:disabled {
    color: $TEXT_LIGHT;
    background-color: $SURFACE_ALT;
    border: 1px solid $ROW_LINE;
}

QLineEdit#SearchBar {
    border-radius: 22px;
    padding: 9px 18px;
}

QComboBox {
    padding: 9px 38px 9px 14px;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 34px;
    border: none;
    background: transparent;
}

QComboBox::down-arrow {
    image: url(@ASSETS@/chevron_down_$THEME.svg);
    width: 14px;
    height: 14px;
}

QComboBox QAbstractItemView {
    background-color: $CARD;
    color: $TEXT;
    border: 1px solid $CARD_BORDER_HOVER;
    border-radius: 12px;
    padding: 6px;
    outline: 0;
    selection-background-color: $SOFT;
    selection-color: $SOFT_TEXT;
}

QDateEdit, QDoubleSpinBox, QSpinBox {
    padding: 7px 40px 7px 14px;
}

QDateEdit::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 36px;
    border: none;
    background: transparent;
}

QDateEdit::down-arrow {
    image: url(@ASSETS@/calendar_$THEME.svg);
    width: 18px;
    height: 18px;
}

QDoubleSpinBox::up-button, QSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 28px;
    border: none;
    background: transparent;
    margin: 4px 6px 0px 0px;
}

QDoubleSpinBox::down-button, QSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 28px;
    border: none;
    background: transparent;
    margin: 0px 6px 4px 0px;
}

QDoubleSpinBox::up-button:hover, QSpinBox::up-button:hover,
QDoubleSpinBox::down-button:hover, QSpinBox::down-button:hover {
    background-color: $SOFT;
    border-radius: 8px;
}

QDoubleSpinBox::up-arrow, QSpinBox::up-arrow {
    image: url(@ASSETS@/chevron_up_$THEME.svg);
    width: 10px;
    height: 10px;
}

QDoubleSpinBox::down-arrow, QSpinBox::down-arrow {
    image: url(@ASSETS@/chevron_down_$THEME.svg);
    width: 10px;
    height: 10px;
}

/* ---------------- Calendar popup ---------------- */

QCalendarWidget {
    background-color: $CARD;
    border: 1px solid $CARD_BORDER_HOVER;
    border-radius: 14px;
}

QCalendarWidget QWidget {
    background-color: $CARD;
    color: $TEXT;
}

QCalendarWidget QWidget#qt_calendar_navigationbar {
    background-color: $SOFT;
    border-top-left-radius: 14px;
    border-top-right-radius: 14px;
    padding: 4px;
}

QCalendarWidget QToolButton {
    color: $SOFT_TEXT;
    background-color: transparent;
    border: none;
    border-radius: 9px;
    padding: 6px 10px;
    font-weight: 700;
}

QCalendarWidget QToolButton:hover {
    background-color: $SOFT_BORDER;
}

QCalendarWidget QToolButton#qt_calendar_prevmonth {
    qproperty-icon: url(@ASSETS@/chevron_left_$THEME.svg);
    icon-size: 16px;
    min-width: 28px;
}

QCalendarWidget QToolButton#qt_calendar_nextmonth {
    qproperty-icon: url(@ASSETS@/chevron_right_$THEME.svg);
    icon-size: 16px;
    min-width: 28px;
}

QCalendarWidget QToolButton::menu-indicator {
    image: none;
    width: 0px;
}

QCalendarWidget QSpinBox {
    color: $TEXT;
    background-color: $CARD;
    border: 1px solid $SOFT_BORDER;
    border-radius: 9px;
    min-width: 92px;
    padding: 2px 28px 2px 8px;
    font-weight: 700;
}

QCalendarWidget QAbstractItemView:enabled {
    background-color: $CARD;
    color: $TEXT;
    selection-background-color: $PRIMARY;
    selection-color: #FFFFFF;
    outline: 0;
}

QCalendarWidget QAbstractItemView:disabled {
    color: $TEXT_LIGHT;
}

QCalendarWidget QTableView QHeaderView::section,
QCalendarWidget QHeaderView::section {
    background-color: $CARD;
    color: $SOFT_TEXT;
    border: none;
    padding: 6px;
    font-weight: 700;
}

#SearchBarContainer {
    background-color: transparent;
}

/* ---------------- Progress ---------------- */

QProgressBar {
    background-color: $TRACK;
    border: none;
    border-radius: 6px;
    min-height: 12px;
    max-height: 12px;
    text-align: center;
}

QProgressBar::chunk {
    background: $G_VIOLET_H;
    border-radius: 6px;
}

QProgressBar[tone="green"]::chunk {
    background: $G_GREEN_H;
}

QProgressBar[tone="pink"]::chunk {
    background: $G_PINK_H;
}

QProgressBar[thin="true"] {
    min-height: 7px;
    max-height: 7px;
    border-radius: 4px;
}

QProgressBar[thin="true"]::chunk {
    border-radius: 4px;
}

/* ---------------- Tables ---------------- */

QTableWidget {
    background: transparent;
    border: none;
    outline: 0;
    gridline-color: transparent;
    selection-background-color: transparent;
}

QHeaderView {
    background: transparent;
    border: none;
}

QHeaderView::section {
    background-color: transparent;
    color: $TEXT_LIGHT;
    padding: 12px 14px;
    border: none;
    border-bottom: 1px solid $ROW_LINE;
    font-weight: 700;
    font-size: 12px;
}

QTableCornerButton::section {
    background: transparent;
    border: none;
}

QTableWidget::item {
    padding: 0px 14px;
    border-bottom: 1px solid $ROW_LINE;
    color: $TEXT;
}

QTableWidget::item:hover {
    background-color: $ROW_HOVER;
}

QTableWidget::item:selected {
    background-color: $ROW_SELECTED;
    color: $SOFT_TEXT_STRONG;
}

#EmptyState {
    background: transparent;
}

#EmptyTitle {
    color: $TEXT;
    font-size: 16px;
    font-weight: 800;
}

#EmptyHint {
    color: $TEXT_LIGHT;
    font-size: 13px;
}

/* ---------------- Scrollbars ---------------- */

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 4px 2px 4px 2px;
}

QScrollBar::handle:vertical {
    background: $SCROLL_HANDLE;
    border-radius: 3px;
    min-height: 34px;
}

QScrollBar::handle:vertical:hover {
    background: $PRIMARY;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}

QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 2px 4px 2px 4px;
}

QScrollBar::handle:horizontal {
    background: $SCROLL_HANDLE;
    border-radius: 3px;
    min-width: 34px;
}

QScrollBar::handle:horizontal:hover {
    background: $PRIMARY;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: transparent;
}

/* ---------------- Typography ---------------- */

QLabel#PageTitle {
    color: $TEXT;
    font-size: 26px;
    font-weight: 800;
}

QLabel#PageSubtitle {
    color: $TEXT_LIGHT;
    font-size: 14px;
}

QLabel#DialogTitle {
    color: $TEXT;
    font-size: 21px;
    font-weight: 800;
}

QLabel#DialogSubtitle {
    color: $TEXT_LIGHT;
    font-size: 13px;
}

QLabel#FilterLabel {
    color: $TEXT_LIGHT;
    font-size: 12px;
    font-weight: 700;
}

QDialog QLabel {
    color: $TEXT_LIGHT;
    font-weight: 600;
}

QTextEdit {
    line-height: 145%;
}

/* ---------------- Dialogs / message boxes ---------------- */

QMessageBox {
    background-color: $BACKGROUND;
}

QMessageBox QLabel {
    color: $TEXT;
    font-size: 14px;
    font-weight: 500;
}

QMessageBox QPushButton {
    background-color: $CARD;
    color: $TEXT;
    border: 1px solid $INPUT_BORDER;
    border-radius: 14px;
    padding: 8px 22px;
    min-width: 72px;
    font-weight: 700;
}

QMessageBox QPushButton:hover {
    background-color: $SOFT;
    border: 1px solid $SOFT_BORDER;
    color: $SOFT_TEXT;
}

QMessageBox QPushButton:default {
    background: $G_VIOLET_H;
    color: #FFFFFF;
    border: 1px solid $PRIMARY_BTN_BORDER;
}

QRadioButton {
    background-color: transparent;
    color: $TEXT;
    spacing: 10px;
    font-weight: 600;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 9px;
}

QRadioButton::indicator:checked {
    background-color: $PRIMARY;
    border: 4px solid $SOFT;
}

QRadioButton::indicator:unchecked {
    background-color: $INPUT_BG;
    border: 2px solid $INPUT_BORDER_HOVER;
}

QCheckBox#ToggleSwitch {
    background-color: transparent;
    spacing: 0;
}

/* ---------------- AI assistant ---------------- */

#AIUserBubble {
    background: $G_VIOLET;
    border: 1px solid $PRIMARY_BTN_BORDER;
    border-radius: 22px;
}

#AIAssistantBubble {
    background-color: $SURFACE_ALT;
    border: 1px solid $CARD_BORDER;
    border-radius: 22px;
}

#AIMessageRole {
    color: $SOFT_TEXT;
    font-size: 12px;
    font-weight: 800;
}

#AIMessageRoleUser {
    color: rgba(255, 255, 255, 190);
    font-size: 12px;
    font-weight: 800;
}

#AIMessageText {
    color: $TEXT;
    font-size: 14px;
}

#AIMessageTextUser {
    color: #FFFFFF;
    font-size: 14px;
}

#AITyping {
    color: $SOFT_TEXT;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 10px;
}

#AISectionLabel {
    color: $TEXT_LIGHT;
    font-size: 12px;
    font-weight: 800;
    margin-top: 4px;
}

#AIProductCard {
    background-color: $CARD;
    border: 1px solid $CARD_BORDER;
    border-radius: 18px;
}

#AIProductTitle {
    color: $TEXT;
    font-size: 14px;
    font-weight: 800;
}

#AIProductPrice {
    color: $SOFT_TEXT;
    font-size: 16px;
    font-weight: 800;
}

#AIProductMeta {
    color: $TEXT_LIGHT;
    font-size: 12px;
}

/* ---------------- Login / splash ---------------- */

#LoginRoot, #SplashRoot {
    background: $G_CANVAS;
}

#LoginShell {
    background-color: $CARD;
    border: 1px solid $CARD_BORDER;
    border-radius: 32px;
}

#LoginHero {
    background: $G_LOGIN_HERO;
    border: 1px solid $HERO_BORDER;
    border-radius: 26px;
}

#LoginHeroTitle {
    color: #FFFFFF;
    font-size: 30px;
    font-weight: 800;
}

#LoginHeroText {
    color: rgba(255, 255, 255, 195);
    font-size: 14px;
}

#LoginFeatureTitle {
    color: #FFFFFF;
    font-size: 13px;
    font-weight: 700;
}

#LoginFeatureText {
    color: rgba(255, 255, 255, 175);
    font-size: 11px;
}

#LoginTitle {
    color: $TEXT;
    font-size: 28px;
    font-weight: 800;
}

#LoginError {
    color: $DANGER;
    background-color: $PILL_RED_BG;
    border: 1px solid $PILL_RED_BORDER;
    border-radius: 12px;
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 600;
}

#SplashCard {
    background: $G_LOGIN_HERO;
    border: 1px solid $HERO_BORDER;
    border-radius: 36px;
}

#SplashTitle {
    color: #FFFFFF;
    font-size: 30px;
    font-weight: 800;
}

#SplashSubtitle {
    color: rgba(255, 255, 255, 200);
    font-size: 14px;
}
$DARK_EXTRAS
"""

DARK_EXTRAS = r"""
/* ---------------- Dark-only refinements ---------------- */

/* luminous edge on raised surfaces */
#Card:hover, #ChartCard:hover {
    border: 1px solid $CARD_BORDER_HOVER;
}

QTableWidget::item:selected {
    border-bottom: 1px solid $SOFT_BORDER;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {
    border: 1px solid $PRIMARY;
}

QPushButton#SecondaryButton {
    background-color: $SURFACE_ALT;
}

QToolButton#SortButton, QToolButton#IconButton, QToolButton#ThemeToggle {
    background-color: $SURFACE_ALT;
}
"""


def build(theme):
    p = colors.get_palette(theme)
    dark = theme == "dark"

    t = {k: v for k, v in p.items() if isinstance(v, str)}
    t["THEME"] = theme
    t["THEME_NAME"] = "Dark" if dark else "Light"
    t["FONT"] = "Segoe UI"

    # gradients
    t["G_CANVAS"] = lg(p["CANVAS_A"], p["CANVAS_B"])
    t["G_SIDEBAR"] = "qlineargradient(x1:0, y1:0, x2:0.7, y2:1, stop:0 %s, stop:1 %s)" % (
        p["SIDEBAR_A"], p["SIDEBAR_B"])
    t["G_VIOLET"] = lg(p["GRAD_A"], p["GRAD_B"])
    t["G_VIOLET_H"] = lg(p["GRAD_A"], p["GRAD_B"], horizontal=True)
    t["G_VIOLET_HOVER"] = lg(shade(p["GRAD_A"], 1.08), shade(p["GRAD_B"], 1.12))
    t["G_VIOLET_H_HOVER"] = lg(shade(p["GRAD_A"], 1.10), shade(p["GRAD_B"], 1.14), horizontal=True)
    t["G_VIOLET_H_PRESSED"] = lg(shade(p["GRAD_A"], 0.9), shade(p["GRAD_B"], 0.88), horizontal=True)
    t["G_VIOLET_SOFT"] = lg(shade(p["GRAD_A"], 1.06), shade(p["GRAD_B"], 1.0))
    t["G_PINK"] = lg(p["PINK_A"], p["PINK_B"])
    t["G_PINK_H"] = lg(p["PINK_A"], p["PINK_B"], horizontal=True)
    t["G_GREEN_H"] = lg(p["GREEN_A"], p["GREEN_B"], horizontal=True)
    danger_a = p["DANGER"] if not dark else "#EE4B5A"
    danger_b = shade(danger_a, 0.78)
    t["G_DANGER_H"] = lg(danger_a, danger_b, horizontal=True)
    t["G_DANGER_H_HOVER"] = lg(shade(danger_a, 1.08), shade(danger_b, 1.1), horizontal=True)
    t["G_DANGER_H_PRESSED"] = lg(shade(danger_a, 0.9), shade(danger_b, 0.85), horizontal=True)
    t["G_HERO"] = lg(p["GRAD_A"], p["GRAD_B"], mid=shade(p["GRAD_A"], 0.9) if not dark else shade(p["GRAD_A"], 0.82))
    t["G_LOGIN_HERO"] = ("qlineargradient(x1:0, y1:0, x2:0.8, y2:1, stop:0 %s, stop:0.6 %s, stop:1 %s)" % (
        p["SIDEBAR_A"], shade(p["SIDEBAR_A"], 0.82), p["SIDEBAR_B"]))

    # derived tokens
    t["HERO_BORDER"] = "rgba(255, 255, 255, 70)" if not dark else "rgba(255, 255, 255, 34)"
    t["HERO_BORDER_PINK"] = "rgba(255, 255, 255, 80)" if not dark else "rgba(255, 255, 255, 40)"
    t["PRIMARY_BTN_BORDER"] = "rgba(255, 255, 255, 60)" if not dark else "rgba(255, 255, 255, 36)"
    t["DANGER_BTN_BORDER"] = "rgba(255, 255, 255, 50)"
    t["CARD_HOVER"] = "#FEFEFF" if not dark else "#1A1B44"
    t["INPUT_FOCUS_BG"] = "#FFFFFF" if not dark else "#13142F"
    t["SOFT_TEXT_STRONG"] = p["ACCENT"] if not dark else "#EDEAFF"
    t["SCROLL_HANDLE"] = "#D6D2F2" if not dark else "#3A3B78"
    t["TOOLTIP_BG"] = "#1C1A3A" if not dark else "#2A2B66"
    t["TOOLTIP_TEXT"] = "#FFFFFF"
    t["TOOLTIP_BORDER"] = "#1C1A3A" if not dark else "#4B47A6"

    if dark:
        t.update(
            PILL_PINK_BG="#3B1D45", PILL_PINK_BORDER="#6A2E66", PILL_PINK_TEXT="#FF9CC6",
            PILL_GREEN_BG="#123A33", PILL_GREEN_BORDER="#1F6B54", PILL_GREEN_TEXT="#5EE0A5",
            PILL_AMBER_BG="#3F3114", PILL_AMBER_BORDER="#7A5A1D", PILL_AMBER_TEXT="#F7C860",
            PILL_RED_BG="#401B26", PILL_RED_BORDER="#7A2C3C",
        )
    else:
        t.update(
            PILL_PINK_BG="#FDE7F0", PILL_PINK_BORDER="#F9CFE0", PILL_PINK_TEXT="#D8467E",
            PILL_GREEN_BG="#E3F6EC", PILL_GREEN_BORDER="#C4EBD6", PILL_GREEN_TEXT="#1E8E57",
            PILL_AMBER_BG="#FFF1D9", PILL_AMBER_BORDER="#FBE0B0", PILL_AMBER_TEXT="#B97609",
            PILL_RED_BG="#FDE8E8", PILL_RED_BORDER="#F9CACB",
        )

    css = TEMPLATE.replace("$DARK_EXTRAS", DARK_EXTRAS if dark else "")

    def sub(match):
        key = match.group(1)
        if key not in t:
            raise KeyError(f"Missing token: {key}")
        return t[key]

    # longest-first safe replace of $TOKEN occurrences
    css = re.sub(r"\$([A-Z][A-Z0-9_]*)", sub, css)

    # Qt quirk: a `border:` shorthand inside a state/attribute rule resets the
    # base rule's border-radius. Use `border-color:` there so corners stay round.
    def fix_block(m):
        selector, body = m.group(1), m.group(2)
        if (":" in selector or "[" in selector) and "chunk" not in selector:
            body = re.sub(r"border:\s*\S+\s+solid\s+([^;]+);", r"border-color: \1;", body)
        return selector + "{" + body + "}"

    css = re.sub(r"([^{}]+)\{([^{}]*)\}", fix_block, css)
    return css.strip() + "\n"


if __name__ == "__main__":
    for theme in ("light", "dark"):
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{theme}.qss")
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(build(theme))
        print("wrote", out)
