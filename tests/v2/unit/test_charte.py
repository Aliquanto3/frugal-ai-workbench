"""Charte générique v2.1 sur l'interface web : valeurs des jetons, sombre d'abord, contrastes des
couples de l'interface (4,5:1 le texte, 3:1 les marques non textuelles), aucun bleu en aplat de
bouton, polices de la charte. Bibliothèque standard seulement, aucun navigateur."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

STATIC = Path(__file__).resolve().parents[3] / "src" / "frugal_ai_workbench" / "web" / "static"
TOKENS = (STATIC / "tokens.css").read_text(encoding="utf-8")

# Valeurs v2.1 (charte-generique, skills/charte/dist/charte.css) des rôles que l'interface emploie.
DARK = {
    "--color-primary": "#8DB0F7",  # primaire
    "--color-button": "#E8ECF2",  # bouton
    "--color-button-hover": "#FFFFFF",  # bouton-survol
    "--color-on-button": "#0F1318",  # sur-bouton
    "--color-focus": "#9EC0FF",  # focus
    "--color-surface": "#0F1318",  # fond
    "--color-surface-alt": "#1E242C",  # surface-alt
    "--color-ink": "#E8ECF2",  # texte
    "--color-ink-secondary": "#A3ADBA",  # texte-attenue
    "--color-gray-graphic": "#8792A0",  # neutre
    "--color-line": "#333B46",  # trait
    "--color-line-strong": "#67717E",  # trait-fort
    "--color-link": "#8DB0F7",  # primaire
    "--color-accent-green": "#8CC7A0",  # succes
    "--color-risk": "#EE8C84",  # erreur
    "--color-alert": "#F0A35E",  # alerte-texte
    "--color-accent": "#E3C26B",  # accent
    "--color-accent-fill": "#E3C26B",  # accent-aplat
    "--color-chart-1": "#8DB0F7",  # cat-1
    "--color-chart-2": "#E3C26B",  # cat-2
    "--color-chart-3": "#8CC7A0",  # cat-3
    "--color-chart-4": "#E58FB8",  # cat-4
    "--color-action-tint": "#1A2742",  # primaire-doux
}
LIGHT = {
    "--color-primary": "#1D5BC2",
    "--color-button": "#121821",
    "--color-button-hover": "#2A3442",
    "--color-on-button": "#FFFFFF",
    "--color-focus": "#1F5FD1",
    "--color-surface": "#F6F8FB",
    "--color-surface-alt": "#ECF0F5",
    "--color-ink": "#121821",
    "--color-ink-secondary": "#4F5A68",
    "--color-gray-graphic": "#6E7886",
    "--color-line": "#CED5DF",
    "--color-line-strong": "#808A97",
    "--color-link": "#1D5BC2",
    "--color-accent-green": "#1B7043",
    "--color-risk": "#B3261E",
    "--color-alert": "#9A4A00",
    "--color-accent": "#8F6300",
    "--color-accent-fill": "#E0B54A",
    "--color-chart-1": "#1D5BC2",
    "--color-chart-2": "#A87A00",
    "--color-chart-3": "#1F8155",
    "--color-chart-4": "#B83A75",
    "--color-action-tint": "#E1EAFA",
}

# Couples (premier plan, fond) de l'interface. Texte : 4,5:1.
TEXT_PAIRS = [
    ("ink", "surface"),
    ("ink", "surface-alt"),
    ("ink", "action-tint"),
    ("ink-secondary", "surface"),
    ("ink-secondary", "surface-alt"),
    ("primary", "surface"),
    ("primary", "surface-alt"),
    ("link", "surface"),
    ("link", "surface-alt"),
    ("accent-green", "surface"),
    ("accent-green", "surface-alt"),
    ("risk", "surface"),
    ("risk", "surface-alt"),
    ("alert", "surface"),
    ("alert", "surface-alt"),
    ("on-button", "button"),
    ("on-button", "button-hover"),
]
# Marques non textuelles : contour des champs (line-strong, gray-graphic), focus, points, pastilles
# et icônes : 3:1. Le filet or du titre est décoratif : hors liste.
NON_TEXT_PAIRS = [
    ("line-strong", "surface"),
    ("line-strong", "surface-alt"),
    ("gray-graphic", "surface"),
    ("gray-graphic", "surface-alt"),
    ("focus", "surface"),
    ("focus", "surface-alt"),
    ("primary", "action-tint"),
    ("alert", "action-tint"),
    ("accent", "surface"),
    ("accent", "surface-alt"),
    ("chart-1", "surface"),
    ("chart-2", "surface"),
    ("chart-3", "surface"),
    ("chart-4", "surface"),
    ("chart-1", "surface-alt"),
    ("chart-2", "surface-alt"),
    ("chart-3", "surface-alt"),
    ("chart-4", "surface-alt"),
    ("button", "surface"),
    ("button", "surface-alt"),
]


def declarations(block: str) -> dict[str, str]:
    block = re.sub(r"/\*.*?\*/", "", block, flags=re.S)
    return {
        name: " ".join(value.split())
        for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", block)
    }


def blocks() -> dict[str, dict[str, str]]:
    """Les trois blocs de couleurs de tokens.css : sombre, clair système, clair forcé."""
    dark = re.search(r"^:root \{(.*?)^\}", TOKENS, re.S | re.M)
    system = re.search(
        r"@media \(prefers-color-scheme: light\) \{\s*:root:not\(\[data-theme\]\) \{(.*?)\n  \}",
        TOKENS,
        re.S,
    )
    forced = re.search(r':root\[data-theme="light"\] \{(.*?)^\}', TOKENS, re.S | re.M)
    assert dark and system and forced
    return {
        "dark": declarations(dark.group(1)),
        "system": declarations(system.group(1)),
        "light": declarations(forced.group(1)),
    }


def luminance(color: str) -> float:
    channels = [int(color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a: str, b: str) -> float:
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def test_contrast_helper_matches_known_ratios():
    assert contrast("#" + "00" * 3, "#" + "FF" * 3) == pytest.approx(21.0)
    assert contrast("#" + "76" * 3, "#" + "FF" * 3) == pytest.approx(4.54, abs=0.01)


def test_dark_is_the_default_and_light_is_a_variant():
    assert re.search(r"^:root \{\s*color-scheme: dark;", TOKENS, re.M)
    assert ':root[data-theme="dark"]' not in TOKENS  # le sombre est déjà en :root
    forced = TOKENS[TOKENS.index(':root[data-theme="light"]') :]
    assert "color-scheme: light;" in forced


def test_dark_and_light_values_are_the_charte_v21_ones():
    found = blocks()
    for name, expected in (("dark", DARK), ("light", LIGHT), ("system", LIGHT)):
        actual = {key: found[name].get(key, "").upper() for key in expected}
        assert actual == expected, name


def test_the_system_light_block_equals_the_forced_light_block():
    found = blocks()
    colors = {k: v for k, v in found["light"].items() if k.startswith("--color-")}
    assert {k: v for k, v in found["system"].items() if k.startswith("--color-")} == colors


@pytest.mark.parametrize("theme", ["dark", "light"])
@pytest.mark.parametrize(("fg", "bg"), TEXT_PAIRS)
def test_text_pairs_keep_four_and_a_half_to_one(theme, fg, bg):
    values = DARK if theme == "dark" else LIGHT
    ratio = contrast(values[f"--color-{fg}"], values[f"--color-{bg}"])
    assert ratio >= 4.5, f"{theme} : {fg} sur {bg} = {ratio:.2f}:1"


@pytest.mark.parametrize("theme", ["dark", "light"])
@pytest.mark.parametrize(("fg", "bg"), NON_TEXT_PAIRS)
def test_non_text_pairs_keep_three_to_one(theme, fg, bg):
    values = DARK if theme == "dark" else LIGHT
    ratio = contrast(values[f"--color-{fg}"], values[f"--color-{bg}"])
    assert ratio >= 3, f"{theme} : {fg} sur {bg} = {ratio:.2f}:1"


def css_rules():
    for path in sorted(STATIC.rglob("*.css")):
        text = re.sub(r"/\*.*?\*/", "", path.read_text(encoding="utf-8"), flags=re.S)
        for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", text):
            yield path.name, " ".join(selector.split()), body


BUTTONISH = re.compile(r"button|btn|launch|install|\bsend\b|switch|segment|toggle", re.I)


def test_le_bleu_n_est_jamais_un_aplat_de_bouton():
    offenders = [
        f"{name} : {selector}"
        for name, selector, body in css_rules()
        if BUTTONISH.search(selector)
        and re.search(r"background(-color)?\s*:[^;]*var\(--color-(primary|link)\)", body)
    ]
    assert offenders == []
    css = "".join(p.read_text(encoding="utf-8") for p in STATIC.rglob("*.css"))
    assert "--color-primary-fill" not in css


def test_buttons_filled_with_the_neutral_button_token_exist():
    filled = [s for _, s, body in css_rules() if "background: var(--color-button)" in body]
    assert ".arena-launch" in filled and ".models-install-reranker" in filled


def test_focus_ring_uses_the_focus_token():
    base = (STATIC / "base.css").read_text(encoding="utf-8")
    assert re.search(r":focus-visible \{\s*outline: 3px solid var\(--color-focus\);", base)
    for path in STATIC.rglob("*.css"):
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"outline:[^;]*var\(--color-primary\)", text), path.name


def test_the_home_title_carries_the_gold_rule():
    screens = (STATIC / "screens.css").read_text(encoding="utf-8")
    block = re.search(r"\.home-title::after \{(.*?)\}", screens, re.S)
    assert block and "var(--color-accent-fill)" in block.group(1)
    assert 'element("h1", "home-title"' in (STATIC / "screens/home.js").read_text(encoding="utf-8")


def test_fonts_are_the_charte_ones_served_locally_with_their_licenses():
    base = (STATIC / "base.css").read_text(encoding="utf-8")
    faces = re.findall(
        r'font-family: "([^"]+)";.*?font-weight: (\d+);.*?url\("([^"]+)"\)', base, re.S
    )
    assert [(family, weight) for family, weight, _ in faces] == [
        ("Atkinson Hyperlegible", "400"),
        ("Atkinson Hyperlegible", "700"),
        ("Sora", "600"),
        ("JetBrains Mono", "400"),
    ]
    for _, _, url in faces:
        assert (STATIC / url.removeprefix("/static/")).stat().st_size > 5_000, url
    for licence in ("OFL-atkinsonhyperlegible", "OFL-sora", "OFL-jetbrainsmono"):
        text = (STATIC / f"fonts/{licence}.txt").read_text(encoding="utf-8")
        assert "SIL OPEN FONT LICENSE" in text.upper()
    assert sorted(p.name for p in (STATIC / "fonts").glob("*.woff2")) == sorted(
        Path(url).name for _, _, url in faces
    )
    found = blocks()["dark"]
    assert found["--font-body"].startswith("'Atkinson Hyperlegible'")
    assert found["--font-heading"].startswith("Sora,")
    assert found["--font-code"].startswith("'JetBrains Mono'")
    assert not re.search(r"Inter", TOKENS + base)
