"""
GURPS Character Sheet Builder  (bilingual: English / Russian)
============================================================

A desktop app (Tkinter) for building a GURPS 4th-edition character sheet.

The interface language is chosen at startup:
    python gurps_character_sheet.py --lang en
    python gurps_character_sheet.py --lang ru
or programmatically via run("en") / run("ru").  The two packaged executables
(GURPS-Sheet-EN.exe, GURPS-Sheet-RU.exe) are thin wrappers that call run() with
the matching language.

Features: live-recalculating attributes & secondary characteristics, a
remaining-points budget with a full breakdown window, thrust/swing damage, a
portrait slot, free-text blocks (Advantages, Disadvantages, Skills, Magic,
Equipment, Notes), save/load as .json, and export to PNG or PDF -- all in a
fantasy parchment-and-leather theme.
"""

import json
import math
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageDraw, ImageFont, ImageTk


# --------------------------------------------------------------------------- #
#  Localization
# --------------------------------------------------------------------------- #

STRINGS = {
    "en": {
        "window_title": "GURPS Character Sheet Builder",
        "banner": "⚔   G U R P S   C H A R A C T E R   F O R G E   ⚔",
        "btn_new": "New", "btn_open": "Open...", "btn_save": "Save...",
        "btn_png": "Export PNG", "btn_pdf": "Export PDF",
        "breakdown_hint": "click for breakdown →",
        "points_left": "◆  {n} pts left",
        "sec_identity": "Identity", "sec_primary": "Primary Attributes",
        "sec_secondary": "Secondary Characteristics", "sec_details": "Details",
        "f_name": "Name", "f_player": "Player", "f_height": "Height",
        "f_weight": "Weight", "f_age": "Age", "f_appearance": "Appearance",
        "attr_st": "ST  Strength", "attr_dx": "DX  Dexterity",
        "attr_iq": "IQ  Intelligence", "attr_ht": "HT  Health",
        "dmg_readout": "Thrust  {thrust}        Swing  {swing}",
        "autoscale_hint": "Auto-scale from attributes; edit to buy up/down.",
        "sec_hp": "HP  Hit Points", "sec_will": "Will",
        "sec_per": "Per  Perception", "sec_fp": "FP  Fatigue",
        "sec_speed": "Basic Speed", "sec_move": "Basic Move",
        "blk_adv": "Advantages & Perks", "blk_disadv": "Disadvantages & Quirks",
        "blk_skills": "Skills", "blk_magic": "Magic & Spells",
        "blk_equip": "Equipment", "blk_notes": "Notes",
        "portrait": "Portrait", "load_portrait": "Load Portrait...",
        "clear": "Clear", "derived_live": "Derived Stats (live)",
        "no_portrait": "＋\nClick to insert image",
        "banner_sub": "~   F o r g e   y o u r   l e g e n d   ~",
        "card_combat": "Combat & Damage", "card_enc": "Encumbrance",
        "v_dodge": "Dodge", "v_thrust": "Thrust",
        "v_swing": "Swing", "v_lift": "Basic Lift",
        "pts_spent_line": "Spent  {spent} / {budget}",
        "combat_dodge": "Dodge", "combat_lift": "Basic Lift",
        "combat_thrust": "Thrust dmg", "combat_swing": "Swing dmg",
        "sum_hp": "HP  Hit Points", "sum_will": "Will",
        "sum_per": "Per  Perception", "sum_fp": "FP  Fatigue",
        "sum_speed": "Basic Speed", "sum_move": "Basic Move",
        "sum_dodge": "Dodge", "sum_thrust": "Thrust damage",
        "sum_swing": "Swing damage", "sum_lift": "Basic Lift",
        "sum_points": "Points spent",
        "enc_header": "Encumbrance  MaxWt  Move Dodge",
        "enc_none": "None", "enc_light": "Light", "enc_medium": "Medium",
        "enc_heavy": "Heavy", "enc_xheavy": "X-Heavy",
        "tbl_level": "Level", "tbl_maxweight": "Max Weight",
        "tbl_move": "Move", "tbl_dodge": "Dodge",
        "pts_title": "Points Breakdown",
        "pts_start": "Starting / Campaign points:",
        "pts_costbreak": "Cost breakdown",
        "pts_othersrc": "Other sources  (advantages +cost, disadvantages −give)",
        "pts_source": "Source", "pts_points": "Points",
        "pts_addsource": "+ Add source", "pts_newsource": "New source",
        "pts_attr_sub": "Attributes subtotal", "pts_sec_sub": "Secondary subtotal",
        "pts_other_sub": "Other sources",
        "pts_total": "Total spent: {spent} pts      Points left: {left}",
        "dlg_new_title": "New Character", "dlg_new_msg": "Discard current character?",
        "dlg_saved": "Saved", "dlg_saved_to": "Saved to:\n{path}",
        "dlg_error": "Error", "dlg_load_err": "Could not load file:\n{e}",
        "dlg_exported": "Exported", "dlg_png_to": "Saved PNG to:\n{path}",
        "dlg_pdf_to": "Saved PDF to:\n{path}", "dlg_export_fail": "Export failed:\n{e}",
        "ft_choose_portrait": "Choose a portrait image",
        "ft_images": "Images", "ft_all": "All files",
        "ft_gurps_char": "GURPS character", "ft_png": "PNG image",
        "ft_pdf": "PDF document",
        "r_attributes": "ATTRIBUTES", "r_secondary": "SECONDARY CHARACTERISTICS",
        "r_combat": "COMBAT", "r_encumbrance": "ENCUMBRANCE",
        "r_adv": "ADVANTAGES & PERKS", "r_disadv": "DISADVANTAGES & QUIRKS",
        "r_skills": "SKILLS", "r_magic": "MAGIC & SPELLS",
        "r_equip": "EQUIPMENT", "r_notes": "NOTES",
        "r_points": "Points", "r_player": "Player", "r_age": "Age",
        "r_height": "Height", "r_weight": "Weight", "r_appearance": "Appearance",
        "r_portrait": "Portrait", "r_footer": "GURPS Character Sheet",
        "r_unnamed": "Unnamed Character",
        "lb": "lb",
    },
    "ru": {
        "window_title": "Конструктор персонажа GURPS",
        "banner": "⚔   КУЗНИЦА   ПЕРСОНАЖА   GURPS   ⚔",
        "btn_new": "Создать", "btn_open": "Открыть...",
        "btn_save": "Сохранить...",
        "btn_png": "Экспорт PNG", "btn_pdf": "Экспорт PDF",
        "breakdown_hint": "нажмите для разбора →",
        "points_left": "◆  осталось {n} оч.",
        "sec_identity": "Сведения",
        "sec_primary": "Основные атрибуты",
        "sec_secondary": "Вторичные характеристики",
        "sec_details": "Подробности",
        "f_name": "Имя", "f_player": "Игрок",
        "f_height": "Рост", "f_weight": "Вес",
        "f_age": "Возраст", "f_appearance": "Внешность",
        "attr_st": "СЛ  Сила", "attr_dx": "ЛВ  Ловкость",
        "attr_iq": "ИН  Интеллект", "attr_ht": "ЗД  Здоровье",
        "dmg_readout": "Укол  {thrust}        Замах  {swing}",
        "autoscale_hint": "Масштабируются от атрибутов; измените, чтобы купить выше/ниже.",
        "sec_hp": "ОЖ  Очки жизни", "sec_will": "Воля",
        "sec_per": "Вн  Внимание", "sec_fp": "ОУ  Очки усталости",
        "sec_speed": "Баз. скорость", "sec_move": "Баз. движение",
        "blk_adv": "Преимущества и перки",
        "blk_disadv": "Недостатки и причуды",
        "blk_skills": "Навыки", "blk_magic": "Магия и заклинания",
        "blk_equip": "Снаряжение", "blk_notes": "Заметки",
        "portrait": "Портрет", "load_portrait": "Загрузить портрет...",
        "clear": "Очистить", "derived_live": "Производные (вживую)",
        "no_portrait": "＋\nНажмите, чтобы вставить",
        "banner_sub": "~   В ы к у й   с в о ю   л е г е н д у   ~",
        "card_combat": "Бой и урон", "card_enc": "Нагрузка",
        "v_dodge": "Уклонение", "v_thrust": "Укол",
        "v_swing": "Замах", "v_lift": "Баз. подъём",
        "pts_spent_line": "Потрачено  {spent} / {budget}",
        "combat_dodge": "Уклонение", "combat_lift": "Баз. подъём",
        "combat_thrust": "Урон укол", "combat_swing": "Урон замах",
        "sum_hp": "ОЖ  Очки жизни", "sum_will": "Воля",
        "sum_per": "Вн  Внимание", "sum_fp": "ОУ  Усталость",
        "sum_speed": "Баз. скорость", "sum_move": "Баз. движение",
        "sum_dodge": "Уклонение", "sum_thrust": "Урон укол",
        "sum_swing": "Урон замах", "sum_lift": "Баз. подъём",
        "sum_points": "Потрачено очков",
        "enc_header": "Нагрузка   Макс   Движ Укл",
        "enc_none": "Нет", "enc_light": "Лёгкая",
        "enc_medium": "Средняя", "enc_heavy": "Тяжёлая",
        "enc_xheavy": "Оч.тяжёлая",
        "tbl_level": "Уровень", "tbl_maxweight": "Макс. вес",
        "tbl_move": "Движ.", "tbl_dodge": "Укл.",
        "pts_title": "Разбор очков",
        "pts_start": "Стартовые очки:",
        "pts_costbreak": "Разбор стоимости",
        "pts_othersrc": "Прочие источники  (преим. +, недост. −)",
        "pts_source": "Источник", "pts_points": "Очки",
        "pts_addsource": "+ Добавить", "pts_newsource": "Новый источник",
        "pts_attr_sub": "Итог атрибутов", "pts_sec_sub": "Итог вторичных",
        "pts_other_sub": "Прочие источники",
        "pts_total": "Потрачено: {spent} оч.      Осталось: {left}",
        "dlg_new_title": "Новый персонаж",
        "dlg_new_msg": "Сбросить текущего персонажа?",
        "dlg_saved": "Сохранено", "dlg_saved_to": "Сохранено в:\n{path}",
        "dlg_error": "Ошибка", "dlg_load_err": "Не удалось загрузить файл:\n{e}",
        "dlg_exported": "Экспорт", "dlg_png_to": "PNG сохранён в:\n{path}",
        "dlg_pdf_to": "PDF сохранён в:\n{path}",
        "dlg_export_fail": "Ошибка экспорта:\n{e}",
        "ft_choose_portrait": "Выберите изображение портрета",
        "ft_images": "Изображения", "ft_all": "Все файлы",
        "ft_gurps_char": "Персонаж GURPS", "ft_png": "Изображение PNG",
        "ft_pdf": "Документ PDF",
        "r_attributes": "АТРИБУТЫ",
        "r_secondary": "ВТОРИЧНЫЕ ХАРАКТЕРИСТИКИ",
        "r_combat": "БОЙ", "r_encumbrance": "НАГРУЗКА",
        "r_adv": "ПРЕИМУЩЕСТВА И ПЕРКИ",
        "r_disadv": "НЕДОСТАТКИ И ПРИЧУДЫ",
        "r_skills": "НАВЫКИ", "r_magic": "МАГИЯ И ЗАКЛИНАНИЯ",
        "r_equip": "СНАРЯЖЕНИЕ", "r_notes": "ЗАМЕТКИ",
        "r_points": "Очки", "r_player": "Игрок", "r_age": "Возраст",
        "r_height": "Рост", "r_weight": "Вес", "r_appearance": "Внешность",
        "r_portrait": "Портрет", "r_footer": "Лист персонажа GURPS",
        "r_unnamed": "Безымянный персонаж",
        "lb": "фунт",
    },
}

LANG = "en"


def set_lang(code):
    global LANG
    LANG = code if code in STRINGS else "en"


def t(key, **kw):
    table = STRINGS.get(LANG, STRINGS["en"])
    s = table.get(key) or STRINGS["en"].get(key, key)
    return s.format(**kw) if kw else s


# --------------------------------------------------------------------------- #
#  GURPS rules helpers
# --------------------------------------------------------------------------- #

# Canonical thrust / swing damage table (GURPS Basic Set), ST 1-40.
_DAMAGE_TABLE = {
    1: ("1d-6", "1d-5"), 2: ("1d-6", "1d-5"), 3: ("1d-5", "1d-4"),
    4: ("1d-5", "1d-4"), 5: ("1d-4", "1d-3"), 6: ("1d-4", "1d-3"),
    7: ("1d-3", "1d-2"), 8: ("1d-3", "1d-2"), 9: ("1d-2", "1d-1"),
    10: ("1d-2", "1d"), 11: ("1d-1", "1d+1"), 12: ("1d-1", "1d+2"),
    13: ("1d", "2d-1"), 14: ("1d", "2d"), 15: ("1d+1", "2d+1"),
    16: ("1d+1", "2d+2"), 17: ("1d+2", "3d-1"), 18: ("1d+2", "3d"),
    19: ("2d-1", "3d+1"), 20: ("2d-1", "3d+2"), 21: ("2d", "4d-1"),
    22: ("2d", "4d"), 23: ("2d+1", "4d+1"), 24: ("2d+1", "4d+2"),
    25: ("2d+2", "5d-1"), 26: ("2d+2", "5d"), 27: ("3d-1", "5d+1"),
    28: ("3d-1", "5d+2"), 29: ("3d", "6d-1"), 30: ("3d", "6d"),
    31: ("3d+1", "6d+1"), 32: ("3d+1", "6d+2"), 33: ("3d+2", "7d-1"),
    34: ("3d+2", "7d"), 35: ("4d-1", "7d+1"), 36: ("4d-1", "7d+2"),
    37: ("4d", "8d-1"), 38: ("4d", "8d"), 39: ("4d+1", "8d+1"),
    40: ("4d+1", "8d+2"),
}


def damage_for_st(st):
    """Return (thrust, swing) damage strings for a Strength value."""
    if st < 1:
        return ("-", "-")
    if st in _DAMAGE_TABLE:
        return _DAMAGE_TABLE[st]
    return _DAMAGE_TABLE[40]


def basic_lift(st):
    """Basic Lift in pounds = ST^2 / 5 (rounded)."""
    return round((st * st) / 5.0)


# Encumbrance: (key, multiple-of-BL, move multiplier, dodge penalty)
ENCUMBRANCE = [
    ("enc_none", 1, 1.0, 0),
    ("enc_light", 2, 0.8, -1),
    ("enc_medium", 3, 0.6, -2),
    ("enc_heavy", 6, 0.4, -3),
    ("enc_xheavy", 10, 0.2, -4),
]

# Point cost per level for each attribute / secondary characteristic.
COST_ST = 10
COST_DX = 20
COST_IQ = 20
COST_HT = 10
COST_HP = 2     # per +1 HP
COST_FP = 3     # per +1 FP
COST_WILL = 5   # per +1 Will
COST_PER = 5    # per +1 Per
COST_SPEED = 5  # per +0.25 Basic Speed
COST_MOVE = 5   # per +1 Basic Move


# --------------------------------------------------------------------------- #
#  Data model
# --------------------------------------------------------------------------- #

class Character:
    """Holds raw input and computes all derived statistics and point costs."""

    def __init__(self):
        self.name = ""
        self.player = ""
        self.height = ""
        self.weight = ""
        self.age = ""
        self.appearance = ""
        self.start_points = 150

        self.st = 10
        self.dx = 10
        self.iq = 10
        self.ht = 10

        self.hp_mod = 0
        self.will_mod = 0
        self.per_mod = 0
        self.fp_mod = 0
        self.speed_mod = 0.0
        self.move_mod = 0

        self.custom_points = []       # list of {"name": str, "points": int}

        self.advantages = ""
        self.disadvantages = ""
        self.skills = ""
        self.magic = ""
        self.equipment = ""
        self.notes = ""

        self.portrait_path = ""

    # --- derived stats -------------------------------------------------- #
    @property
    def hp(self):
        return self.st + self.hp_mod

    @property
    def will(self):
        return self.iq + self.will_mod

    @property
    def per(self):
        return self.iq + self.per_mod

    @property
    def fp(self):
        return self.ht + self.fp_mod

    @property
    def basic_speed(self):
        return (self.ht + self.dx) / 4.0 + self.speed_mod

    @property
    def basic_move(self):
        return max(0, int(math.floor(self.basic_speed)) + self.move_mod)

    @property
    def dodge(self):
        return int(math.floor(self.basic_speed)) + 3

    @property
    def thrust(self):
        return damage_for_st(self.st)[0]

    @property
    def swing(self):
        return damage_for_st(self.st)[1]

    @property
    def basic_lift(self):
        return basic_lift(self.st)

    def encumbrance_rows(self):
        bl = self.basic_lift
        rows = []
        for key, mult, move_mult, dodge_pen in ENCUMBRANCE:
            rows.append({
                "key": key,
                "max_weight": round(bl * mult),
                "move": int(self.basic_move * move_mult),
                "dodge": max(1, self.dodge + dodge_pen),
            })
        return rows

    # --- point costs ---------------------------------------------------- #
    @property
    def st_cost(self):
        return (self.st - 10) * COST_ST

    @property
    def dx_cost(self):
        return (self.dx - 10) * COST_DX

    @property
    def iq_cost(self):
        return (self.iq - 10) * COST_IQ

    @property
    def ht_cost(self):
        return (self.ht - 10) * COST_HT

    @property
    def attribute_points(self):
        return self.st_cost + self.dx_cost + self.iq_cost + self.ht_cost

    @property
    def hp_cost(self):
        return self.hp_mod * COST_HP

    @property
    def fp_cost(self):
        return self.fp_mod * COST_FP

    @property
    def will_cost(self):
        return self.will_mod * COST_WILL

    @property
    def per_cost(self):
        return self.per_mod * COST_PER

    @property
    def speed_cost(self):
        return int(round(self.speed_mod / 0.25)) * COST_SPEED

    @property
    def move_cost(self):
        return self.move_mod * COST_MOVE

    @property
    def secondary_points(self):
        return (self.hp_cost + self.fp_cost + self.will_cost
                + self.per_cost + self.speed_cost + self.move_cost)

    @property
    def custom_points_total(self):
        total = 0
        for e in self.custom_points:
            try:
                total += int(e.get("points", 0))
            except (TypeError, ValueError):
                pass
        return total

    @property
    def total_points(self):
        return (self.attribute_points + self.secondary_points
                + self.custom_points_total)

    # --- persistence ---------------------------------------------------- #
    _FIELDS = (
        "name", "player", "height", "weight", "age", "appearance",
        "start_points", "st", "dx", "iq", "ht", "hp_mod", "will_mod",
        "per_mod", "fp_mod", "speed_mod", "move_mod", "custom_points",
        "advantages", "disadvantages", "skills", "magic", "equipment",
        "notes", "portrait_path",
    )

    def to_dict(self):
        return {k: getattr(self, k) for k in self._FIELDS}

    def from_dict(self, data):
        for k, v in data.items():
            if k in self._FIELDS:
                setattr(self, k, v)
        if not isinstance(self.custom_points, list):
            self.custom_points = []


# --------------------------------------------------------------------------- #
#  Sheet renderer (Pillow) -> PNG / PDF export
# --------------------------------------------------------------------------- #

def _load_font(size, bold=False):
    # Serif faces (with Cyrillic coverage) for a fantasy / old-manuscript feel.
    # Candidates are tried in order and cover Windows, macOS and Linux.
    if bold:
        candidates = [
            "georgiab.ttf",                                            # Windows
            "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",    # macOS
            "/Library/Fonts/Georgia Bold.ttf",
            "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
            "timesbd.ttf", "arialbd.ttf",
            "DejaVuSerif-Bold.ttf",                                   # Linux
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        ]
    else:
        candidates = [
            "georgia.ttf",                                            # Windows
            "/System/Library/Fonts/Supplemental/Georgia.ttf",        # macOS
            "/Library/Fonts/Georgia.ttf",
            "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
            "times.ttf", "arial.ttf",
            "DejaVuSerif.ttf",                                       # Linux
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        ]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_sheet(char, scale=2):
    """Render the character to a Pillow Image and return it."""
    W, H = 850 * scale, 1100 * scale
    img = Image.new("RGB", (W, H), (233, 219, 194))   # aged parchment
    d = ImageDraw.Draw(img)

    d.rectangle([10 * scale, 10 * scale, W - 10 * scale, H - 10 * scale],
                outline=(74, 53, 30), width=4 * scale)
    d.rectangle([16 * scale, 16 * scale, W - 16 * scale, H - 16 * scale],
                outline=(122, 90, 46), width=1 * scale)

    f_title = _load_font(28 * scale, bold=True)
    f_head = _load_font(15 * scale, bold=True)
    f_label = _load_font(11 * scale, bold=True)
    f_text = _load_font(11 * scale)
    f_big = _load_font(20 * scale, bold=True)

    margin = 34 * scale
    ink = (43, 30, 16)
    accent = (90, 62, 33)

    def text(x, y, s, font=f_text, fill=ink):
        d.text((x, y), s, font=font, fill=fill)

    def box(x0, y0, x1, y1, width=2):
        d.rectangle([x0, y0, x1, y1], outline=accent, width=width)

    # --- header ---------------------------------------------------------- #
    text(margin, margin, char.name or t("r_unnamed"), f_title, accent)
    d.line([margin, margin + 44 * scale, W - margin, margin + 44 * scale],
           fill=accent, width=2 * scale)

    y = margin + 54 * scale
    pts = f"{t('r_points')}: {char.total_points}"
    if char.start_points:
        pts += f" / {char.start_points}"
    id_line = [pts]
    for label_key, val in (("r_player", char.player), ("r_age", char.age),
                           ("r_height", char.height), ("r_weight", char.weight)):
        if val:
            id_line.append(f"{t(label_key)}: {val}")
    text(margin, y, "    ".join(id_line), f_text)
    if char.appearance:
        text(margin, y + 16 * scale, f"{t('r_appearance')}: {char.appearance}", f_text)

    # --- portrait -------------------------------------------------------- #
    port_w, port_h = 200 * scale, 240 * scale
    px0 = W - margin - port_w
    py0 = margin + 110 * scale
    box(px0, py0, px0 + port_w, py0 + port_h)
    if char.portrait_path and os.path.exists(char.portrait_path):
        try:
            p = Image.open(char.portrait_path).convert("RGB")
            p.thumbnail((port_w - 6 * scale, port_h - 6 * scale))
            img.paste(p, (px0 + (port_w - p.width) // 2,
                          py0 + (port_h - p.height) // 2))
        except Exception:
            text(px0 + 20 * scale, py0 + port_h // 2, "(x)", f_text)
    else:
        text(px0 + port_w // 2 - 30 * scale, py0 + port_h // 2 - 8 * scale,
             t("r_portrait"), f_label, (150, 125, 95))

    # --- attributes block ------------------------------------------------ #
    ax0, ay0 = margin, py0
    col_w, row_h = 150 * scale, 34 * scale

    def stat_cell(col, row, label, value, big=False):
        x0 = ax0 + col * (col_w + 10 * scale)
        y0 = ay0 + row * (row_h + 8 * scale)
        box(x0, y0, x0 + col_w, y0 + row_h, width=2)
        text(x0 + 8 * scale, y0 + 6 * scale, label, f_label, accent)
        vf = f_big if big else f_head
        d.text((x0 + col_w - 12 * scale, y0 + (4 if big else 6) * scale),
               str(value), font=vf, fill=ink, anchor="ra")

    text(ax0, ay0 - 22 * scale, t("r_attributes"), f_head, accent)
    stat_cell(0, 0, t("attr_st"), char.st, big=True)
    stat_cell(1, 0, t("attr_dx"), char.dx, big=True)
    stat_cell(0, 1, t("attr_iq"), char.iq, big=True)
    stat_cell(1, 1, t("attr_ht"), char.ht, big=True)

    # --- secondary characteristics --------------------------------------- #
    sy = ay0 + 2 * (row_h + 8 * scale) + 24 * scale
    text(ax0, sy - 22 * scale, t("r_secondary"), f_head, accent)
    secondaries = [
        (t("sec_hp"), char.hp), (t("sec_will"), char.will),
        (t("sec_per"), char.per), (t("sec_fp"), char.fp),
        (t("sec_speed"), f"{char.basic_speed:.2f}"), (t("sec_move"), char.basic_move),
    ]
    for i, (label, value) in enumerate(secondaries):
        col, row = i % 2, i // 2
        x0 = ax0 + col * (col_w + 10 * scale)
        y0 = sy + row * (row_h + 8 * scale)
        box(x0, y0, x0 + col_w, y0 + row_h, width=2)
        text(x0 + 8 * scale, y0 + 9 * scale, label, f_label, accent)
        d.text((x0 + col_w - 12 * scale, y0 + 6 * scale),
               str(value), font=f_head, fill=ink, anchor="ra")

    # --- combat / damage ------------------------------------------------- #
    cy = sy + 3 * (row_h + 8 * scale) + 24 * scale
    text(ax0, cy - 22 * scale, t("r_combat"), f_head, accent)
    combat = [
        (t("combat_dodge"), char.dodge), (t("combat_lift"), f"{char.basic_lift} {t('lb')}"),
        (t("combat_thrust"), char.thrust), (t("combat_swing"), char.swing),
    ]
    for i, (label, value) in enumerate(combat):
        col, row = i % 2, i // 2
        x0 = ax0 + col * (col_w + 10 * scale)
        y0 = cy + row * (row_h + 8 * scale)
        box(x0, y0, x0 + col_w, y0 + row_h, width=2)
        text(x0 + 8 * scale, y0 + 9 * scale, label, f_label, accent)
        d.text((x0 + col_w - 12 * scale, y0 + 6 * scale),
               str(value), font=f_head, fill=ink, anchor="ra")

    # --- encumbrance table ----------------------------------------------- #
    ey = max(cy + 2 * (row_h + 8 * scale) + 30 * scale,
             py0 + port_h + 30 * scale)
    text(margin, ey - 22 * scale, t("r_encumbrance"), f_head, accent)
    headers = [t("tbl_level"), t("tbl_maxweight"), t("tbl_move"), t("tbl_dodge")]
    cw = (W - 2 * margin) / 4
    box(margin, ey, W - margin, ey + 18 * scale)
    for i, htxt in enumerate(headers):
        text(margin + i * cw + 6 * scale, ey + 3 * scale, htxt, f_label, accent)
    ry = ey + 18 * scale
    for row in char.encumbrance_rows():
        vals = [t(row["key"]), f"{row['max_weight']} {t('lb')}",
                str(row["move"]), str(row["dodge"])]
        box(margin, ry, W - margin, ry + 18 * scale, width=1)
        for i, v in enumerate(vals):
            text(margin + i * cw + 6 * scale, ry + 3 * scale, v, f_text)
        ry += 18 * scale

    # --- text blocks ----------------------------------------------------- #
    def wrap(s, font, max_w):
        out = []
        for raw_line in s.splitlines() or [""]:
            words, line = raw_line.split(" "), ""
            for w in words:
                trial = (line + " " + w).strip()
                if d.textlength(trial, font=font) <= max_w:
                    line = trial
                else:
                    if line:
                        out.append(line)
                    line = w
            out.append(line)
        return out

    block_y = ry + 26 * scale
    blocks = [
        (t("r_adv"), char.advantages), (t("r_disadv"), char.disadvantages),
        (t("r_skills"), char.skills), (t("r_magic"), char.magic),
        (t("r_equip"), char.equipment), (t("r_notes"), char.notes),
    ]
    for title, body in blocks:
        if block_y > H - 60 * scale:
            break
        text(margin, block_y, title, f_head, accent)
        block_y += 20 * scale
        for line in wrap(body or "-", f_text, W - 2 * margin):
            if block_y > H - 30 * scale:
                break
            text(margin + 6 * scale, block_y, line, f_text)
            block_y += 15 * scale
        block_y += 12 * scale

    d.line([margin, H - 30 * scale, W - margin, H - 30 * scale],
           fill=(150, 120, 90), width=1)
    text(margin, H - 26 * scale, t("r_footer"), f_text, (140, 112, 80))
    return img


# --------------------------------------------------------------------------- #
#  Fantasy theme palette (browns, near-black, cream-white)
# --------------------------------------------------------------------------- #
COL_DARK = "#241a10"
COL_LEATHER = "#3a2a1a"
COL_BROWN = "#6b4a2b"
COL_BROWN_LT = "#8a6a45"
COL_PARCH = "#e9dcc0"
COL_CARD = "#efe6cd"
COL_FIELD = "#f7f0dd"
COL_INK = "#2a1c0e"
COL_CREAM = "#f7efda"
COL_GOLD = "#a87f37"
COL_GOLD_LT = "#caa258"
COL_BRONZE = "#7a5320"

FONT_BODY = ("Georgia", 10)
FONT_HEAD = ("Georgia", 11, "bold")


class App(tk.Tk):
    _INT_KEYS = ("st", "dx", "iq", "ht")
    _TEXT_KEYS = ("advantages", "disadvantages", "skills", "magic",
                  "equipment", "notes")

    def __init__(self):
        super().__init__()
        self.title(t("window_title"))
        self.geometry("1140x860")
        self.minsize(1040, 700)

        self.char = Character()
        self._portrait_img = None
        # Suppressed during construction: classic tk.Spinbox fires its variable
        # trace as it is created, before all widgets exist. _sync_from_char
        # clears this once the UI is fully built.
        self._suppress = True
        self.vars = {}
        self.sec_vars = {}
        self.sec_base = {}
        self.sec_mod = {}
        self.points_win = None
        self._points_refresh = None

        self._apply_theme()
        self._build_ui()
        self._sync_from_char()
        self.recalc()

    # ----- theme --------------------------------------------------------- #
    def _apply_theme(self):
        self.configure(bg=COL_DARK)
        st = ttk.Style(self)
        st.theme_use("clam")
        st.configure(".", background=COL_PARCH, foreground=COL_INK, font=FONT_BODY)
        st.configure("TFrame", background=COL_PARCH)
        st.configure("TLabel", background=COL_PARCH, foreground=COL_INK, font=FONT_BODY)
        st.configure("Sub.TLabel", foreground=COL_BROWN, font=("Georgia", 9, "italic"))
        st.configure("Value.TLabel", foreground=COL_BRONZE,
                     font=("Georgia", 12, "bold"))
        st.configure("Head.TLabel", foreground=COL_DARK, font=("Georgia", 11, "bold"))
        st.configure("TButton", background=COL_BROWN, foreground=COL_CREAM,
                     font=("Georgia", 10, "bold"), borderwidth=2,
                     relief="raised", padding=6, focuscolor=COL_GOLD_LT)
        st.map("TButton",
               background=[("active", COL_BROWN_LT), ("pressed", COL_LEATHER)],
               foreground=[("disabled", "#9b8a70")])
        st.configure("TEntry", fieldbackground=COL_FIELD, foreground=COL_INK,
                     bordercolor=COL_BROWN, insertcolor=COL_INK,
                     lightcolor=COL_BROWN, darkcolor=COL_BROWN, padding=3)
        st.configure("TSpinbox", fieldbackground=COL_FIELD, foreground=COL_INK,
                     bordercolor=COL_BROWN, arrowcolor=COL_BROWN,
                     insertcolor=COL_INK, lightcolor=COL_BROWN, darkcolor=COL_BROWN)
        st.configure("Attr.TSpinbox", fieldbackground=COL_FIELD, foreground=COL_INK,
                     bordercolor=COL_GOLD, arrowcolor=COL_BROWN,
                     lightcolor=COL_GOLD, darkcolor=COL_GOLD,
                     font=("Georgia", 15, "bold"))
        st.configure("Sec.TSpinbox", fieldbackground=COL_FIELD, foreground=COL_INK,
                     bordercolor=COL_BROWN, arrowcolor=COL_BROWN,
                     lightcolor=COL_BROWN, darkcolor=COL_BROWN,
                     font=("Georgia", 11, "bold"))
        st.configure("TSeparator", background=COL_GOLD)
        st.configure("TLabelframe", background=COL_PARCH, bordercolor=COL_GOLD,
                     relief="ridge", borderwidth=2)
        st.configure("TLabelframe.Label", background=COL_PARCH,
                     foreground=COL_BRONZE, font=("Georgia", 11, "bold"))
        st.configure("Vertical.TScrollbar", background=COL_BROWN,
                     troughcolor=COL_PARCH, bordercolor=COL_LEATHER,
                     arrowcolor=COL_CREAM)
        st.map("Vertical.TScrollbar", background=[("active", COL_BROWN_LT)])

    # ----- UI construction ---------------------------------------------- #
    def _build_ui(self):
        root = ttk.Frame(self, padding=8)
        root.pack(fill="both", expand=True, padx=6, pady=6)

        # --- ornamented banner --- #
        banner = tk.Frame(root, bg=COL_DARK)
        banner.pack(fill="x")
        tk.Label(banner, text=t("banner"), bg=COL_DARK, fg=COL_CREAM,
                 font=("Georgia", 16, "bold"), pady=(8)).pack(pady=(8, 0))
        tk.Label(banner, text=t("banner_sub"), bg=COL_DARK, fg=COL_GOLD_LT,
                 font=("Georgia", 9, "italic")).pack(pady=(0, 8))
        tk.Frame(root, bg=COL_GOLD, height=3).pack(fill="x", pady=(0, 8))

        bar = ttk.Frame(root)
        bar.pack(fill="x", pady=(0, 8))
        ttk.Button(bar, text=t("btn_new"), command=self.new_char).pack(side="left")
        ttk.Button(bar, text=t("btn_open"), command=self.load_json).pack(side="left", padx=4)
        ttk.Button(bar, text=t("btn_save"), command=self.save_json).pack(side="left")
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Button(bar, text=t("btn_png"), command=self.export_png).pack(side="left")
        ttk.Button(bar, text=t("btn_pdf"), command=self.export_pdf).pack(side="left", padx=4)

        self.points_btn = tk.Button(
            bar, text="◆  0", command=self.open_points,
            font=("Georgia", 12, "bold"), bg=COL_DARK, fg=COL_CREAM,
            activebackground=COL_LEATHER, activeforeground=COL_CREAM,
            relief="ridge", bd=3, padx=14, pady=3, cursor="hand2")
        self.points_btn.pack(side="right")
        ttk.Label(bar, text=t("breakdown_hint"),
                  style="Sub.TLabel").pack(side="right", padx=6)

        body = ttk.Frame(root)
        body.pack(fill="both", expand=True)
        self._active_canvas = None
        # Mouse wheel: <MouseWheel> on Windows/macOS, <Button-4/5> on Linux.
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<Button-4>", self._on_mousewheel)
        self.bind_all("<Button-5>", self._on_mousewheel)

        # Reserve the right panel's fixed width FIRST. Pack order matters: by
        # claiming the right side before the form, the form can only take the
        # leftover space and can never squeeze the panel off-screen.
        self.combat_vars = {}
        self.enc_vars = []
        right = ttk.Frame(body, width=396)
        right.pack(side="right", fill="y", padx=(10, 0))
        right.pack_propagate(False)
        rinner = self._scrollable(right)   # right panel scrolls independently

        # --- left: scrollable card form, fills the remaining width --- #
        left = ttk.Frame(body)
        left.pack(side="left", fill="both", expand=True)
        self.form = self._scrollable(left)
        self._build_form(self.form)

        # --- right panel cards (into the scrollable inner frame) --- #
        pcard = ttk.LabelFrame(rinner, text=t("portrait"), padding=8)
        pcard.pack(fill="x")
        self.portrait_label = tk.Label(pcard, height=11,
                                       bg=COL_FIELD, fg=COL_BROWN,
                                       font=("Georgia", 11, "italic"),
                                       relief="ridge", bd=3, cursor="hand2")
        self.portrait_label.pack(fill="both")
        self.portrait_label.bind("<Button-1>", lambda e: self.load_portrait())
        pbtns = ttk.Frame(pcard)
        pbtns.pack(fill="x", pady=(8, 0))
        ttk.Button(pbtns, text=t("load_portrait"),
                   command=self.load_portrait).pack(side="left")
        ttk.Button(pbtns, text=t("clear"),
                   command=self.clear_portrait).pack(side="left", padx=4)

        ccard = ttk.LabelFrame(rinner, text=t("card_combat"), padding=10)
        ccard.pack(fill="x", pady=(10, 0))
        ccard.columnconfigure(1, weight=1)
        for i, (name_key, vkey) in enumerate(
                [("v_dodge", "dodge"), ("v_thrust", "thrust"),
                 ("v_swing", "swing"), ("v_lift", "lift")]):
            ttk.Label(ccard, text=t(name_key)).grid(row=i, column=0, sticky="w", pady=3)
            var = tk.StringVar()
            self.combat_vars[vkey] = var
            ttk.Label(ccard, textvariable=var, style="Value.TLabel").grid(
                row=i, column=1, sticky="e", pady=3)

        ecard = ttk.LabelFrame(rinner, text=f"{t('card_enc')}  ({t('lb')})",
                               padding=(10, 8))
        ecard.pack(fill="x", pady=(10, 0))
        ecard.columnconfigure(0, weight=1)              # level name stretches
        for col in (1, 2, 3):
            ecard.columnconfigure(col, minsize=54)
        enc_heads = [t("tbl_level"), t("tbl_maxweight"),
                     t("tbl_move"), t("tbl_dodge")]
        for col, htext in enumerate(enc_heads):
            ttk.Label(ecard, text=htext, font=("Georgia", 8, "bold"),
                      foreground=COL_BRONZE,
                      anchor=("w" if col == 0 else "e")).grid(
                row=0, column=col, sticky="ew", padx=3, pady=(0, 3))
        ttk.Separator(ecard, orient="horizontal").grid(
            row=1, column=0, columnspan=4, sticky="ew", pady=(0, 3))
        for r in range(5):
            rowvars = []
            for col in range(4):
                var = tk.StringVar()
                bold = "bold" if col == 0 else "normal"
                ttk.Label(ecard, textvariable=var,
                          font=("Georgia", 9, bold),
                          foreground=(COL_BRONZE if col == 0 else COL_INK),
                          anchor=("w" if col == 0 else "e")).grid(
                    row=r + 2, column=col, sticky="ew", padx=3, pady=1)
                rowvars.append(var)
            self.enc_vars.append(rowvars)

        self.spent_var = tk.StringVar()
        ttk.Label(rinner, textvariable=self.spent_var, style="Sub.TLabel").pack(
            anchor="e", pady=(10, 6))

    def _scrollable(self, parent):
        """Wrap `parent` with a vertical scrollbar; return the inner frame to
        which content is added. The mouse wheel scrolls whichever scrollable
        region the cursor is currently over."""
        canvas = tk.Canvas(parent, highlightthickness=0, bg=COL_PARCH, width=10)
        vsb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfigure(win_id, width=e.width))
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        canvas.bind("<Enter>", lambda e, c=canvas: setattr(self, "_active_canvas", c))
        return inner

    def _on_mousewheel(self, e):
        c = getattr(self, "_active_canvas", None)
        if c is None:
            return
        num = getattr(e, "num", 0)
        if num == 4:                       # Linux: wheel up
            c.yview_scroll(-1, "units")
        elif num == 5:                     # Linux: wheel down
            c.yview_scroll(1, "units")
        elif e.delta:
            if sys.platform == "darwin":   # macOS deltas are small (±1, ±2…)
                c.yview_scroll(-int(e.delta), "units")
            else:                          # Windows deltas are ±120 per notch
                c.yview_scroll(int(-e.delta / 120), "units")

    def _add_entry(self, parent, label, key):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=3)
        ttk.Label(row, text=label, width=13).pack(side="left")
        var = tk.StringVar()
        var.trace_add("write", lambda *_: self._on_field_change(key, var))
        ttk.Entry(row, textvariable=var).pack(side="left", fill="x", expand=True)
        self.vars[key] = var

    def _tile_spin(self, tile, var, frm, to, inc, font):
        return tk.Spinbox(
            tile, from_=frm, to=to, increment=inc, textvariable=var,
            width=5, justify="center", font=font,
            bg=COL_FIELD, fg=COL_INK, readonlybackground=COL_FIELD,
            insertbackground=COL_INK, buttonbackground=COL_BROWN,
            relief="flat", highlightthickness=1, highlightbackground=COL_BROWN,
            bd=1)

    def _attr_tile(self, parent, key, label, r, c):
        tile = tk.Frame(parent, bg=COL_FIELD, highlightbackground=COL_GOLD,
                        highlightthickness=2)
        tile.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)
        tk.Label(tile, text=label, bg=COL_FIELD, fg=COL_BRONZE,
                 font=("Georgia", 10, "bold")).pack(pady=(8, 2))
        var = tk.StringVar()
        var.trace_add("write", lambda *_: self._on_field_change(key, var))
        self._tile_spin(tile, var, 1, 40, 1, ("Georgia", 17, "bold")).pack(pady=(0, 10))
        self.vars[key] = var

    def _sec_tile(self, parent, key, label, base_fn, mod_attr, frm, to, inc, r, c):
        tile = tk.Frame(parent, bg=COL_FIELD, highlightbackground=COL_BROWN,
                        highlightthickness=1)
        tile.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)
        tk.Label(tile, text=label, bg=COL_FIELD, fg=COL_BRONZE,
                 font=("Georgia", 9, "bold"), wraplength=150,
                 justify="center").pack(pady=(7, 1))
        var = tk.StringVar()
        self.sec_vars[key] = var
        self.sec_base[key] = base_fn
        self.sec_mod[key] = mod_attr
        var.trace_add("write",
                      lambda *_, k=key, v=var: self._on_secondary_change(k, v))
        self._tile_spin(tile, var, frm, to, inc, ("Georgia", 13, "bold")).pack(pady=(0, 8))

    def _add_text(self, parent, label, key, height=4):
        ttk.Label(parent, text=label, font=("Georgia", 9, "bold"),
                  foreground=COL_BRONZE).pack(anchor="w", pady=(8, 1))
        txt = tk.Text(parent, height=height, width=40, wrap="word",
                      bg=COL_FIELD, fg=COL_INK, insertbackground=COL_INK,
                      font=FONT_BODY, relief="ridge", bd=2,
                      highlightthickness=1, highlightbackground=COL_BROWN,
                      highlightcolor=COL_GOLD)
        txt.pack(fill="x")
        txt.bind("<KeyRelease>", lambda e, k=key, w=txt: self._on_text_change(k, w))
        self.vars[key] = txt

    def _build_form(self, f):
        # --- Identity card --- #
        icard = ttk.LabelFrame(f, text=t("sec_identity"), padding=10)
        icard.pack(fill="x", padx=2, pady=(2, 8))
        self._add_entry(icard, t("f_name"), "name")
        self._add_entry(icard, t("f_player"), "player")
        self._add_entry(icard, t("f_height"), "height")
        self._add_entry(icard, t("f_weight"), "weight")
        self._add_entry(icard, t("f_age"), "age")
        self._add_entry(icard, t("f_appearance"), "appearance")

        # --- Primary attributes card (2x2 tiles) --- #
        acard = ttk.LabelFrame(f, text=t("sec_primary"), padding=10)
        acard.pack(fill="x", padx=2, pady=8)
        agrid = ttk.Frame(acard)
        agrid.pack(fill="x")
        agrid.columnconfigure(0, weight=1)
        agrid.columnconfigure(1, weight=1)
        self._attr_tile(agrid, "st", t("attr_st"), 0, 0)
        self._attr_tile(agrid, "dx", t("attr_dx"), 0, 1)
        self._attr_tile(agrid, "iq", t("attr_iq"), 1, 0)
        self._attr_tile(agrid, "ht", t("attr_ht"), 1, 1)

        # --- Secondary characteristics card (2x3 tiles) --- #
        scard = ttk.LabelFrame(f, text=t("sec_secondary"), padding=10)
        scard.pack(fill="x", padx=2, pady=8)
        ttk.Label(scard, text=t("autoscale_hint"), style="Sub.TLabel").pack(anchor="w")
        sgrid = ttk.Frame(scard)
        sgrid.pack(fill="x")
        sgrid.columnconfigure(0, weight=1)
        sgrid.columnconfigure(1, weight=1)
        self._sec_tile(sgrid, "hp", t("sec_hp"), lambda c: c.st, "hp_mod", 1, 80, 1, 0, 0)
        self._sec_tile(sgrid, "will", t("sec_will"), lambda c: c.iq, "will_mod", 1, 40, 1, 0, 1)
        self._sec_tile(sgrid, "per", t("sec_per"), lambda c: c.iq, "per_mod", 1, 40, 1, 1, 0)
        self._sec_tile(sgrid, "fp", t("sec_fp"), lambda c: c.ht, "fp_mod", 1, 80, 1, 1, 1)
        self._sec_tile(sgrid, "speed", t("sec_speed"),
                       lambda c: (c.ht + c.dx) / 4.0, "speed_mod", 0, 30, 0.25, 2, 0)
        self._sec_tile(sgrid, "move", t("sec_move"),
                       lambda c: int(math.floor(c.basic_speed)), "move_mod", 0, 50, 1, 2, 1)

        # --- Details card --- #
        dcard = ttk.LabelFrame(f, text=t("sec_details"), padding=10)
        dcard.pack(fill="x", padx=2, pady=8)
        self._add_text(dcard, t("blk_adv"), "advantages")
        self._add_text(dcard, t("blk_disadv"), "disadvantages")
        self._add_text(dcard, t("blk_skills"), "skills")
        self._add_text(dcard, t("blk_magic"), "magic")
        self._add_text(dcard, t("blk_equip"), "equipment")
        self._add_text(dcard, t("blk_notes"), "notes")

    # ----- data binding -------------------------------------------------- #
    def _on_field_change(self, key, var):
        if self._suppress:
            return
        raw = var.get()
        if key in self._INT_KEYS:
            try:
                setattr(self.char, key, int(float(raw)) if raw not in ("", "-") else 0)
            except ValueError:
                return
        else:
            setattr(self.char, key, raw)
        self.recalc()

    def _on_secondary_change(self, key, var):
        if self._suppress:
            return
        try:
            value = float(var.get())
        except ValueError:
            return
        base = self.sec_base[key](self.char)
        mod_attr = self.sec_mod[key]
        if mod_attr == "speed_mod":
            setattr(self.char, mod_attr, round((value - base) * 4) / 4.0)
        else:
            setattr(self.char, mod_attr, int(round(value - base)))
        self.recalc()

    def _on_text_change(self, key, widget):
        setattr(self.char, key, widget.get("1.0", "end-1c"))

    def _sync_from_char(self):
        self._suppress = True
        try:
            for key, var in self.vars.items():
                if isinstance(var, tk.Text):
                    var.delete("1.0", "end")
                    var.insert("1.0", getattr(self.char, key, ""))
                else:
                    var.set(getattr(self.char, key, ""))
        finally:
            self._suppress = False
        self._show_portrait()

    # ----- live recalculation ------------------------------------------- #
    def recalc(self):
        c = self.char
        self._suppress = True
        try:
            self.sec_vars["hp"].set(c.hp)
            self.sec_vars["will"].set(c.will)
            self.sec_vars["per"].set(c.per)
            self.sec_vars["fp"].set(c.fp)
            self.sec_vars["speed"].set(f"{c.basic_speed:.2f}")
            self.sec_vars["move"].set(c.basic_move)
        finally:
            self._suppress = False

        lb = t("lb")
        self.combat_vars["dodge"].set(c.dodge)
        self.combat_vars["thrust"].set(c.thrust)
        self.combat_vars["swing"].set(c.swing)
        self.combat_vars["lift"].set(f"{c.basic_lift} {lb}")

        for i, r in enumerate(c.encumbrance_rows()):
            self.enc_vars[i][0].set(t(r["key"]))
            self.enc_vars[i][1].set(r["max_weight"])
            self.enc_vars[i][2].set(r["move"])
            self.enc_vars[i][3].set(r["dodge"])

        self.spent_var.set(t("pts_spent_line", spent=c.total_points,
                             budget=c.start_points))

        self._update_points_button()
        if self._points_refresh and self.points_win and self.points_win.winfo_exists():
            self._points_refresh()

    def _update_points_button(self):
        c = self.char
        remaining = c.start_points - c.total_points
        self.points_btn.config(
            text=t("points_left", n=remaining),
            fg=("#e08a6b" if remaining < 0 else COL_CREAM))

    # ----- portrait ------------------------------------------------------ #
    def load_portrait(self):
        path = filedialog.askopenfilename(
            title=t("ft_choose_portrait"),
            filetypes=[(t("ft_images"), "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
                       (t("ft_all"), "*.*")])
        if path:
            self.char.portrait_path = path
            self._show_portrait()

    def clear_portrait(self):
        self.char.portrait_path = ""
        self._show_portrait()

    # Fixed display box for the portrait (pixels). Images are scaled to fit
    # inside it with their aspect ratio preserved and centred -- never stretched.
    PORTRAIT_BOX = (256, 280)

    def _show_portrait(self):
        box_w, box_h = self.PORTRAIT_BOX
        path = self.char.portrait_path
        if path and os.path.exists(path):
            try:
                im = Image.open(path).convert("RGB")
                im.thumbnail((box_w, box_h), Image.LANCZOS)  # keeps aspect ratio
                self._portrait_img = ImageTk.PhotoImage(im)
                # width/height in pixels (image present): box stays fixed, the
                # picture is centred inside it with parchment padding around.
                self.portrait_label.configure(image=self._portrait_img, text="",
                                              width=box_w, height=box_h)
                return
            except Exception:
                pass
        self._portrait_img = None
        # No image: width/height revert to text units (chars / lines).
        self.portrait_label.configure(image="", text=t("no_portrait"),
                                      width=24, height=13)

    # ----- points breakdown dialog -------------------------------------- #
    def open_points(self):
        if self.points_win and self.points_win.winfo_exists():
            self.points_win.lift()
            self.points_win.focus_force()
            return

        win = tk.Toplevel(self)
        self.points_win = win
        win.title(t("pts_title"))
        win.geometry("480x700")
        win.minsize(440, 560)
        win.configure(bg=COL_PARCH)

        top = ttk.Frame(win, padding=(10, 10, 10, 4))
        top.pack(fill="x")
        ttk.Label(top, text=t("pts_start")).pack(side="left")
        sp_var = tk.StringVar(value=str(self.char.start_points))

        def on_sp(*_):
            try:
                self.char.start_points = int(float(sp_var.get() or 0))
            except ValueError:
                return
            self.recalc()
        sp_var.trace_add("write", on_sp)
        ttk.Spinbox(top, from_=0, to=100000, textvariable=sp_var,
                    width=8).pack(side="left", padx=6)

        bd = ttk.LabelFrame(win, text=t("pts_costbreak"), padding=(14, 10))
        bd.pack(fill="x", padx=12, pady=(6, 8))
        bd.columnconfigure(0, weight=1)
        self._bd = {}
        bd_row = [0]

        def add_cost(key, name_text="", sub=False, sep=False):
            if sep:
                ttk.Separator(bd, orient="horizontal").grid(
                    row=bd_row[0], column=0, columnspan=2, sticky="ew", pady=5)
                bd_row[0] += 1
            nv = tk.StringVar(value=name_text)
            vv = tk.StringVar()
            nf = ("Georgia", 10, "bold") if sub else ("Georgia", 10)
            fg = COL_BRONZE if sub else COL_INK
            ttk.Label(bd, textvariable=nv, font=nf, foreground=fg).grid(
                row=bd_row[0], column=0, sticky="w", pady=2)
            # Value column: right-aligned, monospace -> every number (incl. 0)
            # lines up in a single column.
            ttk.Label(bd, textvariable=vv, font=("Consolas", 11, "bold"),
                      foreground=fg, anchor="e", width=6).grid(
                row=bd_row[0], column=1, sticky="e", padx=(16, 0), pady=2)
            self._bd[key] = (nv, vv)
            bd_row[0] += 1

        for k in ("st", "dx", "iq", "ht"):
            add_cost(k)
        add_cost("attr_sub", t("pts_attr_sub"), sub=True)
        for j, k in enumerate(("hp", "fp", "will", "per", "speed", "move")):
            add_cost(k, sep=(j == 0))
        add_cost("sec_sub", t("pts_sec_sub"), sub=True)
        add_cost("other_sub", t("pts_other_sub"), sub=True, sep=True)

        cs = ttk.LabelFrame(win, text=t("pts_othersrc"), padding=8)
        cs.pack(fill="both", expand=True, padx=10)
        head = ttk.Frame(cs)
        head.pack(fill="x")
        ttk.Label(head, text=t("pts_source"), width=26,
                  font=("Georgia", 9, "bold")).pack(side="left")
        ttk.Label(head, text=t("pts_points"),
                  font=("Georgia", 9, "bold")).pack(side="left")
        holder = ttk.Frame(cs)
        holder.pack(fill="both", expand=True, pady=2)

        tot_var = tk.StringVar()
        totbar = tk.Frame(win, bg=COL_DARK)
        totbar.pack(fill="x", padx=12, pady=(4, 10))
        tk.Label(totbar, textvariable=tot_var, bg=COL_DARK, fg=COL_CREAM,
                 font=("Georgia", 11, "bold"), pady=8).pack()

        def refresh():
            c = self.char
            named = {
                "st": (f"ST   {c.st}", c.st_cost),
                "dx": (f"DX   {c.dx}", c.dx_cost),
                "iq": (f"IQ   {c.iq}", c.iq_cost),
                "ht": (f"HT   {c.ht}", c.ht_cost),
                "hp": (f"HP   {c.hp}", c.hp_cost),
                "fp": (f"FP   {c.fp}", c.fp_cost),
                "will": (f"Will  {c.will}", c.will_cost),
                "per": (f"Per   {c.per}", c.per_cost),
                "speed": (f"Speed  {c.basic_speed:.2f}", c.speed_cost),
                "move": (f"Move  {c.basic_move}", c.move_cost),
            }
            for k, (nm, cost) in named.items():
                self._bd[k][0].set(nm)
                self._bd[k][1].set(cost)
            self._bd["attr_sub"][1].set(c.attribute_points)
            self._bd["sec_sub"][1].set(c.secondary_points)
            self._bd["other_sub"][1].set(c.custom_points_total)
            spent = c.total_points
            tot_var.set(t("pts_total", spent=spent, left=c.start_points - spent))
            self._update_points_button()

        def build_rows():
            for w in holder.winfo_children():
                w.destroy()
            for i, entry in enumerate(self.char.custom_points):
                row = ttk.Frame(holder)
                row.pack(fill="x", pady=1)
                nv = tk.StringVar(value=str(entry.get("name", "")))
                pv = tk.StringVar(value=str(entry.get("points", 0)))

                def make_cb(idx, nv, pv):
                    def upd(*_):
                        self.char.custom_points[idx]["name"] = nv.get()
                        try:
                            self.char.custom_points[idx]["points"] = \
                                int(float(pv.get() or 0))
                        except ValueError:
                            pass
                        self.recalc()
                    return upd
                cb = make_cb(i, nv, pv)
                nv.trace_add("write", cb)
                pv.trace_add("write", cb)
                ttk.Entry(row, textvariable=nv, width=26).pack(side="left")
                ttk.Spinbox(row, textvariable=pv, from_=-1000, to=1000,
                            width=7).pack(side="left", padx=4)

                def remove(idx=i):
                    del self.char.custom_points[idx]
                    build_rows()
                    self.recalc()
                ttk.Button(row, text="✕", width=3,
                           command=remove).pack(side="left")
            refresh()

        def add_source():
            self.char.custom_points.append({"name": t("pts_newsource"), "points": 0})
            build_rows()
            self.recalc()
        ttk.Button(cs, text=t("pts_addsource"),
                   command=add_source).pack(anchor="w", pady=(4, 0))

        self._points_refresh = refresh

        def on_close():
            self._points_refresh = None
            win.destroy()
            self.points_win = None
        win.protocol("WM_DELETE_WINDOW", on_close)

        build_rows()

    # ----- file ops ------------------------------------------------------ #
    def new_char(self):
        if messagebox.askyesno(t("dlg_new_title"), t("dlg_new_msg")):
            self.char = Character()
            self._sync_from_char()
            self.recalc()

    def _flush_text_blocks(self):
        for key in self._TEXT_KEYS:
            setattr(self.char, key, self.vars[key].get("1.0", "end-1c"))

    def save_json(self):
        self._flush_text_blocks()
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[(t("ft_gurps_char"), "*.json")],
            initialfile=(self.char.name or "character") + ".json")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.char.to_dict(), fh, indent=2, ensure_ascii=False)
        messagebox.showinfo(t("dlg_saved"), t("dlg_saved_to", path=path))

    def load_json(self):
        path = filedialog.askopenfilename(
            filetypes=[(t("ft_gurps_char"), "*.json"), (t("ft_all"), "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            self.char = Character()
            self.char.from_dict(data)
            self._sync_from_char()
            self.recalc()
        except Exception as e:
            messagebox.showerror(t("dlg_error"), t("dlg_load_err", e=e))

    def export_png(self):
        self._flush_text_blocks()
        path = filedialog.asksaveasfilename(
            defaultextension=".png", filetypes=[(t("ft_png"), "*.png")],
            initialfile=(self.char.name or "character") + ".png")
        if not path:
            return
        try:
            render_sheet(self.char).save(path, "PNG")
            messagebox.showinfo(t("dlg_exported"), t("dlg_png_to", path=path))
        except Exception as e:
            messagebox.showerror(t("dlg_error"), t("dlg_export_fail", e=e))

    def export_pdf(self):
        self._flush_text_blocks()
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[(t("ft_pdf"), "*.pdf")],
            initialfile=(self.char.name or "character") + ".pdf")
        if not path:
            return
        try:
            render_sheet(self.char).save(path, "PDF", resolution=150.0)
            messagebox.showinfo(t("dlg_exported"), t("dlg_pdf_to", path=path))
        except Exception as e:
            messagebox.showerror(t("dlg_error"), t("dlg_export_fail", e=e))


def run(lang="en"):
    set_lang(lang)
    App().mainloop()


if __name__ == "__main__":
    chosen = "en"
    if "--lang" in sys.argv:
        i = sys.argv.index("--lang")
        if i + 1 < len(sys.argv):
            chosen = sys.argv[i + 1]
    run(chosen)
