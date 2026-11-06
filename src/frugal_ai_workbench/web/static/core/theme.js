// Thème et mode projection (UX-DR2). Réglages d'affichage du navigateur seulement : ils vont dans
// `localStorage` (avec les volets et les brouillons, AD-20), jamais au serveur. Chaque accès est
// gardé : sans stockage (fenêtre privée, données bloquées), le choix tient pour la page ouverte.
// Chargé en tête de page avec `blocking="render"` : `data-theme` est posé avant le premier rendu.
//
// Trois choix (D-7) : « Clair », « Sombre » et « Système ». Règle de la charte : le choix mémorisé,
// sinon la préférence du système, sinon le sombre. Sans choix mémorisé, c'est donc « Système », et
// « Système » donne le clair seulement si le système le demande (`prefers-color-scheme: light`).
// `data-theme` de `<html>` porte toujours le jeu de jetons appliqué (`light` ou `dark`) : « Système »
// n'a pas de troisième jeu, il suit le système quand celui-ci change, page ouverte.
// `data-theme-choice` porte le choix de la personne.

const THEME_KEY = "wl.theme";
const PROJECTION_KEY = "wl.projection";
const LIGHT_QUERY = "(prefers-color-scheme: light)";
export const THEMES = ["light", "dark", "system"];

function read(key) {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function write(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch {
    // Pas de stockage : le choix vaut pour cette page seulement.
  }
}

function systemMedia() {
  try {
    return matchMedia(LIGHT_QUERY);
  } catch {
    return null;
  }
}

// Le choix gardé (`light`, `dark` ou `system`), « Système » faute de choix mémorisé.
export function getTheme() {
  const stored = read(THEME_KEY);
  return THEMES.includes(stored) ? stored : "system";
}

// Le jeu de jetons qu'un choix donne : `light` ou `dark`, le sombre faute de préférence du système.
export function appliedTheme(choice) {
  if (choice === "system") return systemMedia()?.matches ? "light" : "dark";
  return choice === "light" ? "light" : "dark";
}

let current = getTheme();

function apply() {
  document.documentElement.dataset.theme = appliedTheme(current);
  document.documentElement.dataset.themeChoice = current;
}

export function setTheme(theme) {
  current = THEMES.includes(theme) ? theme : "system";
  apply();
  write(THEME_KEY, current);
}

export function getProjection() {
  return read(PROJECTION_KEY) === "1";
}

export function setProjection(on) {
  document.documentElement.dataset.projection = on ? "true" : "false";
  write(PROJECTION_KEY, on ? "1" : "0");
}

// Réglages mémorisés, appliqués dès l'import ; « Système » suit les changements du système.
apply();
document.documentElement.dataset.projection = getProjection() ? "true" : "false";
systemMedia()?.addEventListener("change", () => {
  if (current === "system") apply();
});
