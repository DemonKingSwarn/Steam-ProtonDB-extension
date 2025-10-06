export async function injectProtonDB(): Promise<void> {
  // Only run on app pages
  if (!window.location.href.match(/^https:\/\/store\.steampowered\.com\/app\/\d+/)) return;

  const appIdMatch = window.location.href.match(/\/app\/(\d+)/);
  if (!appIdMatch) return;
  const appId = appIdMatch[1];

  // Fetch ProtonDB summary via backend
  const summary = await fetch(`/plugin/protondb/summary/${appId}`).then(r => r.json()).catch(() => null);

  if (!summary || !summary.tier) return;

  // Find where to inject
  const header = document.querySelector('.apphub_AppName') || document.querySelector('.apphub_HeaderStandardTop');
  if (!header) return;

  // Build badge
  const tier = summary.tier;
  const badge = document.createElement('span');
  badge.className = `protondb-badge tier-${tier.toLowerCase()}`;
  badge.innerText = `ProtonDB: ${tier.charAt(0).toUpperCase() + tier.slice(1)}`;
  badge.style.marginLeft = "8px";

  // Add link to ProtonDB
  badge.onclick = () => window.open(`https://protondb.com/app/${appId}`, "_blank");
  badge.style.cursor = "pointer";

  header.appendChild(badge);

  // Deck verification
  if (summary.steamDeck && summary.steamDeck.verification) {
    const deck = document.createElement('span');
    deck.className = "protondb-deck";
    deck.innerText = `Deck: ${summary.steamDeck.verification}`;
    deck.style.marginLeft = "8px";
    header.appendChild(deck);
  }
}
