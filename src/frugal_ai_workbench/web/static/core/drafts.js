// Brouillons de saisie (AD-20) : le texte tapé et pas encore envoyé survit à un rechargement, dans
// `localStorage` seulement (jamais la bascule cloud, qui vit dans le store). Le stockage peut être
// absent ou refusé (fenêtre privée, données bloquées) : chaque accès est protégé, l'écran marche sans.

const PREFIX = "frugal-ai-workbench.draft.";
// Préfixe de l'ancien nom (jusqu'à 2.0.0a8) : un brouillon gardé sous lui passe sous le nouveau
// à la première lecture, puis l'ancienne clé est retirée (un brouillon envoyé ne revient pas).
const LEGACY_PREFIX = "wavelocalai.draft.";

export function loadDraft(name) {
  try {
    const value = localStorage.getItem(PREFIX + name);
    if (value !== null) return value;
    const legacy = localStorage.getItem(LEGACY_PREFIX + name);
    if (legacy === null) return "";
    localStorage.setItem(PREFIX + name, legacy);
    localStorage.removeItem(LEGACY_PREFIX + name);
    return legacy;
  } catch {
    return "";
  }
}

// Un brouillon vide est effacé plutôt que gardé.
export function saveDraft(name, value) {
  try {
    if (value) localStorage.setItem(PREFIX + name, value);
    else localStorage.removeItem(PREFIX + name);
  } catch {
    // Pas de stockage : le brouillon reste dans le champ, c'est tout.
  }
}
