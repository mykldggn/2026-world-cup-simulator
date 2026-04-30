const state = {
  metadata: null,
  teamIndex: {},
  teamProfiles: {},
  latestSimulation: null,
  scenario: "balanced",
};

const CONFED_ASSETS = {
  UEFA: { name: "UEFA", url: "/static/assets/federations/uefa.svg" },
  CONMEBOL: { name: "CONMEBOL", url: "/static/assets/federations/conmebol.svg" },
  Concacaf: { name: "Concacaf", url: "/static/assets/federations/concacaf.svg" },
  AFC: { name: "AFC", url: "/static/assets/federations/afc.svg" },
  CAF: { name: "CAF", url: "/static/assets/federations/caf.svg" },
  OFC: { name: "OFC", url: "/static/assets/federations/ofc.svg" },
};

const TEAM_BADGE_ASSETS = {
  ALG: "/static/assets/teams/ALG.png",
  ARG: "/static/assets/teams/ARG.png",
  AUS: "/static/assets/teams/AUS.png",
  AUT: "/static/assets/teams/AUT.svg",
  BEL: "/static/assets/teams/BEL.svg",
  BIH: "/static/assets/teams/BIH.svg",
  BRA: "/static/assets/teams/BRA.png",
  CAN: "/static/assets/teams/CAN.png",
  CIV: "/static/assets/teams/CIV.png",
  COD: "/static/assets/teams/COD.png",
  COL: "/static/assets/teams/COL.png",
  CPV: "/static/assets/teams/CPV.png",
  CRO: "/static/assets/teams/CRO.svg",
  CUR: "/static/assets/teams/CUR.png",
  CZE: "/static/assets/teams/CZE.svg",
  ECU: "/static/assets/teams/ECU.png",
  EGY: "/static/assets/teams/EGY.png",
  ENG: "/static/assets/teams/ENG.svg",
  ESP: "/static/assets/teams/ESP.svg",
  FRA: "/static/assets/teams/FRA.svg",
  GER: "/static/assets/teams/GER.svg",
  GHA: "/static/assets/teams/GHA.png",
  HAI: "/static/assets/teams/HAI.png",
  IRN: "/static/assets/teams/IRN.png",
  IRQ: "/static/assets/teams/IRQ.png",
  JOR: "/static/assets/teams/JOR.png",
  JPN: "/static/assets/teams/JPN.png",
  KOR: "/static/assets/teams/KOR.png",
  KSA: "/static/assets/teams/KSA.png",
  MAR: "/static/assets/teams/MAR.png",
  MEX: "/static/assets/teams/MEX.png",
  NED: "/static/assets/teams/NED.svg",
  NOR: "/static/assets/teams/NOR.svg",
  NZL: "/static/assets/teams/NZL.png",
  PAN: "/static/assets/teams/PAN.png",
  PAR: "/static/assets/teams/PAR.png",
  POR: "/static/assets/teams/POR.svg",
  QAT: "/static/assets/teams/QAT.png",
  RSA: "/static/assets/teams/RSA.png",
  SCO: "/static/assets/teams/SCO.svg",
  SEN: "/static/assets/teams/SEN.png",
  SUI: "/static/assets/teams/SUI.svg",
  SWE: "/static/assets/teams/SWE.svg",
  TUN: "/static/assets/teams/TUN.png",
  TUR: "/static/assets/teams/TUR.svg",
  URU: "/static/assets/teams/URU.png",
  USA: "/static/assets/teams/USA.png",
  UZB: "/static/assets/teams/UZB.png",
};

const LOCAL_FLAG_ASSETS = {
  "gb-eng": "/static/assets/flags/gb-eng.svg",
  "gb-sct": "/static/assets/flags/gb-sct.svg",
};

const form = document.getElementById("simulation-form");
const iterationsInput = document.getElementById("iterations");
const iterationsOutput = document.getElementById("iterations-output");
const featuredTeamSelect = document.getElementById("featured-team");
const hostAdvantageInput = document.getElementById("host-advantage");
const buildStatus = document.getElementById("build-status");
const modalShell = document.getElementById("team-modal");
const modalContent = document.getElementById("team-modal-content");
const modalCloseButton = document.getElementById("team-modal-close");

iterationsInput.addEventListener("input", () => {
  iterationsOutput.textContent = iterationsInput.value;
});

document.querySelectorAll(".scenario-button").forEach((button) => {
  button.addEventListener("click", () => {
    document
      .querySelectorAll(".scenario-button")
      .forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    state.scenario = button.dataset.scenario;
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  await runSimulation();
});

modalCloseButton.addEventListener("click", closeTeamModal);
modalShell.addEventListener("click", (event) => {
  if (event.target instanceof HTMLElement && event.target.dataset.closeModal === "true") {
    closeTeamModal();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !modalShell.hidden) {
    closeTeamModal();
  }
});

document.addEventListener("click", async (event) => {
  const target = event.target instanceof HTMLElement ? event.target : null;
  if (!target) {
    return;
  }

  const teamTrigger = target.closest("[data-team-code]");
  if (teamTrigger instanceof HTMLElement) {
    openTeamModal(teamTrigger.dataset.teamCode);
    return;
  }

  const actionTrigger = target.closest("[data-share-action]");
  if (!(actionTrigger instanceof HTMLElement)) {
    return;
  }

  if (actionTrigger.dataset.shareAction === "copy") {
    await copyShareSnapshot();
  }
  if (actionTrigger.dataset.shareAction === "download") {
    downloadRunSnapshot();
  }
});

function formatPercent(value) {
  return `${(value * 100).toFixed(1)}%`;
}

function formatSigned(value, decimals = 3) {
  const prefix = value >= 0 ? "+" : "";
  return `${prefix}${Number(value).toFixed(decimals)}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function buildSubdivisionFlag(code) {
  if (code === "gb-eng") {
    return String.fromCodePoint(
      0x1f3f4,
      0xe0067,
      0xe0062,
      0xe0065,
      0xe006e,
      0xe0067,
      0xe007f
    );
  }
  if (code === "gb-sct") {
    return String.fromCodePoint(
      0x1f3f4,
      0xe0067,
      0xe0062,
      0xe0073,
      0xe0063,
      0xe0074,
      0xe007f
    );
  }
  return "";
}

function flagFromCode(code) {
  if (!code) {
    return "";
  }
  if (code.startsWith("gb-")) {
    return buildSubdivisionFlag(code);
  }
  return code
    .toUpperCase()
    .split("")
    .map((character) => String.fromCodePoint(127397 + character.charCodeAt(0)))
    .join("");
}

function flagAssetUrl(code) {
  if (!code) {
    return "";
  }
  if (LOCAL_FLAG_ASSETS[code]) {
    return LOCAL_FLAG_ASSETS[code];
  }
  return `/static/assets/flags/${code.toLowerCase()}.png`;
}

function teamBadgeUrl(team) {
  return TEAM_BADGE_ASSETS[team.code] || "";
}

function getTeam(code) {
  return state.teamProfiles[code] || state.teamIndex[code] || null;
}

function renderTeamIdentity(team, metaText = "") {
  const confedAsset = CONFED_ASSETS[team.confederation];
  const badgeAsset = teamBadgeUrl(team);
  return `
    <div class="team-identity">
      <div class="team-mark-stack">
        <img
          class="team-crest"
          src="${badgeAsset || confedAsset?.url || ""}"
          data-fallback="${confedAsset?.url || ""}"
          alt="${escapeHtml(team.name)} badge"
          loading="lazy"
          referrerpolicy="no-referrer"
          onerror="if(this.dataset.fallback && this.src !== this.dataset.fallback){this.src=this.dataset.fallback;this.dataset.fallback='';}else{this.style.display='none';}"
        >
        <img
          class="team-flag-img"
          src="${flagAssetUrl(team.flagCode)}"
          alt="${escapeHtml(team.name)} flag"
          loading="lazy"
          referrerpolicy="no-referrer"
          onerror="this.replaceWith(Object.assign(document.createElement('span'), {className:'team-flag-fallback', textContent:'${flagFromCode(team.flagCode)}'}))"
        >
      </div>
      <div class="team-text">
        <strong>${escapeHtml(team.name)}</strong>
        <span class="team-meta">
          ${escapeHtml(team.code)} | ${escapeHtml(team.confederation)}${metaText ? ` | ${escapeHtml(metaText)}` : ""}
        </span>
      </div>
    </div>
  `;
}

function renderTeamButton(team, metaText = "", className = "team-button") {
  return `
    <button type="button" class="${className}" data-team-code="${escapeHtml(team.code)}">
      ${renderTeamIdentity(team, metaText)}
    </button>
  `;
}

function renderHero(metadata) {
  const chips = document.getElementById("hero-chips");
  chips.innerHTML = "";
  [
    metadata.format,
    metadata.dates,
    `${metadata.teams.length} qualified teams`,
    `${metadata.groups.length} groups`,
    `FIFA rank snapshot ${metadata.rankingDate}`,
  ].forEach((label) => {
    const chip = document.createElement("span");
    chip.className = "hero-chip";
    chip.textContent = label;
    chips.appendChild(chip);
  });
}

function setText(id, value) {
  const element = document.getElementById(id);
  if (element) {
    element.textContent = value;
  }
}

function renderSummary(summary) {
  const grid = document.getElementById("summary-grid");
  const cards = [
    {
      label: "Favorite",
      value: summary.favorite.name,
      subtext: `FIFA #${summary.favorite.fifaRank} | ${formatPercent(summary.favorite.probability)} title probability`,
    },
    {
      label: "Dark Horse",
      value: summary.darkHorse.name,
      subtext: `FIFA #${summary.darkHorse.fifaRank} | ${formatPercent(summary.darkHorse.probability)} title probability`,
    },
    {
      label: "Goals per Match",
      value: summary.averageGoalsPerMatch.toFixed(2),
      subtext: "Average output across all simulated tournament matches.",
    },
    {
      label: "Most Common Final",
      value: `${summary.mostCommonFinal.teams[0]} vs ${summary.mostCommonFinal.teams[1]}`,
      subtext: `${formatPercent(summary.mostCommonFinal.probability)} of the full run set`,
    },
  ];

  grid.innerHTML = cards
    .map(
      (card) => `
        <article class="metric-card">
          <div class="metric-label">${escapeHtml(card.label)}</div>
          <div class="metric-value">${escapeHtml(card.value)}</div>
          <div class="metric-subtext">${escapeHtml(card.subtext)}</div>
        </article>
      `
    )
    .join("");
}

function renderBreakdownRows(items) {
  const maxContribution = Math.max(...items.map((item) => item.contribution), 0.01);
  return items
    .map(
      (item) => `
        <div class="breakdown-row">
          <div class="breakdown-copy">
            <span>${escapeHtml(item.label)}</span>
            <strong>${item.contribution.toFixed(2)}</strong>
          </div>
          <div class="breakdown-track">
            <div class="breakdown-fill" style="width:${(item.contribution / maxContribution) * 100}%"></div>
          </div>
        </div>
      `
    )
    .join("");
}

function renderSimpleMetricList(title, items, kind = "value") {
  return `
    <div class="mini-panel">
      <h4>${escapeHtml(title)}</h4>
      ${items
        .map((item) => {
          const value =
            kind === "percent"
              ? formatPercent(item.probability)
              : Number(item.value).toFixed(1);
          return `
            <div class="mini-row">
              <span>${escapeHtml(item.label || item.stage || item.opponent)}</span>
              <strong>${escapeHtml(value)}</strong>
            </div>
          `;
        })
        .join("")}
    </div>
  `;
}

function renderFeaturedTeam(featuredTeam) {
  setText(
    "featured-heading",
    `Group ${featuredTeam.group} | FIFA #${featuredTeam.fifaRank} | ${featuredTeam.style}`
  );

  const container = document.getElementById("featured-team-card");
  container.innerHTML = `
    <div class="featured-topline">
      ${renderTeamButton(featuredTeam, `Group ${featuredTeam.group} | FIFA #${featuredTeam.fifaRank}`, "team-button featured-team-button")}
      <button type="button" class="secondary-button" data-team-code="${escapeHtml(featuredTeam.code)}">Open team page</button>
    </div>
    <div class="featured-meta">
      <span class="meta-pill">FIFA #${featuredTeam.fifaRank}</span>
      <span class="meta-pill">Anchor ${featuredTeam.rankingAnchor.toFixed(1)}</span>
      <span class="meta-pill">Power ${featuredTeam.power.toFixed(1)}</span>
      <span class="meta-pill">${escapeHtml(featuredTeam.style)}</span>
      <span class="meta-pill">Group ${featuredTeam.group}</span>
    </div>
    <div class="feature-metrics">
      <div class="feature-metric">
        Advance
        <strong>${formatPercent(featuredTeam.advanceProbability)}</strong>
      </div>
      <div class="feature-metric">
        Quarterfinal
        <strong>${formatPercent(featuredTeam.quarterfinalProbability)}</strong>
      </div>
      <div class="feature-metric">
        Win
        <strong>${formatPercent(featuredTeam.championProbability)}</strong>
      </div>
      <div class="feature-metric">
        Avg Pts
        <strong>${featuredTeam.avgGroupPoints.toFixed(2)}</strong>
      </div>
    </div>
    <div class="featured-insight-grid">
      <div class="mini-panel">
        <h4>Why this team?</h4>
        ${renderBreakdownRows(featuredTeam.powerBreakdown)}
      </div>
      <div class="mini-stack">
        ${renderSimpleMetricList("Strengths", featuredTeam.strengths)}
        ${renderSimpleMetricList("Risks", featuredTeam.risks)}
      </div>
      <div class="mini-stack">
        ${renderSimpleMetricList(
          "Most Likely Knockout Opponents",
          featuredTeam.commonOpponents.map((item) => ({
            label: `${item.stage}: ${item.opponent}`,
            probability: item.probability,
          })),
          "percent"
        )}
      </div>
    </div>
  `;

  const notes = document.getElementById("model-notes");
  notes.innerHTML = featuredTeam.notes
    .map((note) => `<div class="note-item">${escapeHtml(note)}</div>`)
    .join("");
}

function renderScenarioCompare(rows) {
  const container = document.getElementById("scenario-compare");
  container.innerHTML = rows
    .map(
      (row) => `
        <article class="compare-card ${row.active ? "active" : ""}">
          <div class="compare-label-row">
            <span class="metric-label">${escapeHtml(row.label)}</span>
            ${row.active ? '<span class="active-tag">Current</span>' : ""}
          </div>
          <div class="compare-value">${formatPercent(row.titleProbability)}</div>
          <div class="metric-subtext">${escapeHtml(row.featuredTeam)} title odds</div>
          <div class="compare-metrics">
            <div><span>Advance</span><strong>${formatPercent(row.advanceProbability)}</strong></div>
            <div><span>Semifinal</span><strong>${formatPercent(row.semifinalProbability)}</strong></div>
            <div><span>Goals / Match</span><strong>${row.averageGoalsPerMatch.toFixed(2)}</strong></div>
            <div><span>Upset Rate</span><strong>${formatPercent(row.upsetRate)}</strong></div>
          </div>
          <div class="compare-footer">
            Favorite: ${escapeHtml(row.fieldFavorite)} (${formatPercent(row.favoriteProbability)})
          </div>
        </article>
      `
    )
    .join("");
}

function renderShareCard(shareCard) {
  const container = document.getElementById("share-card");
  container.innerHTML = `
    <div class="share-header">
      <h3>${escapeHtml(shareCard.title)}</h3>
      <p id="share-status">Ready to copy or download.</p>
    </div>
    <div class="share-lines">
      ${shareCard.lines.map((line) => `<div class="share-line">${escapeHtml(line)}</div>`).join("")}
    </div>
    <div class="share-actions">
      <button type="button" class="secondary-button" data-share-action="copy">Copy Summary</button>
      <button type="button" class="secondary-button" data-share-action="download">Download JSON</button>
    </div>
  `;
}

function renderUpsetTracker(upsetTracker) {
  const biggest = upsetTracker.biggestUpsetCandidate;
  const container = document.getElementById("upset-tracker");
  container.innerHTML = `
    <div class="signal-header">
      <h3>Upset Tracker</h3>
      <p>Where the bracket feels fragile instead of stable.</p>
    </div>
    <div class="signal-body">
      <div class="signal-stat">
        <span>Biggest upset candidate</span>
        <strong>${biggest ? `${escapeHtml(biggest.winner)} over ${escapeHtml(biggest.loser)}` : "No signal yet"}</strong>
        ${biggest ? `<small>${escapeHtml(biggest.stage)} | ${formatPercent(biggest.probability)} | ${biggest.powerGap.toFixed(1)} power gap</small>` : ""}
      </div>
      <div class="signal-stat">
        <span>Most volatile group</span>
        <strong>Group ${escapeHtml(upsetTracker.mostVolatileGroup.group)}</strong>
        <small>Volatility ${upsetTracker.mostVolatileGroup.volatilityIndex.toFixed(3)} | table repeat ${formatPercent(upsetTracker.mostVolatileGroup.mostLikelyTableProbability)}</small>
      </div>
      <div class="signal-stat">
        <span>Most fragile favorite</span>
        <strong>${escapeHtml(upsetTracker.fragileFavorite.name)}</strong>
        <small>Advance ${formatPercent(upsetTracker.fragileFavorite.advanceProbability)} | QF ${formatPercent(upsetTracker.fragileFavorite.quarterfinalProbability)} | Win ${formatPercent(upsetTracker.fragileFavorite.championProbability)}</small>
      </div>
    </div>
  `;
}

function renderVenueLens(venueLens) {
  const container = document.getElementById("venue-lens");
  container.innerHTML = `
    <div class="signal-header">
      <h3>Venue + Travel</h3>
      <p>${escapeHtml(venueLens.headline)}</p>
    </div>
    <div class="signal-card-grid">
      ${venueLens.cards
        .map(
          (card) => `
            <div class="venue-chip-card">
              <span>${escapeHtml(card.label)}</span>
              <strong>${escapeHtml(card.value)}</strong>
              <small>${escapeHtml(card.detail)}</small>
            </div>
          `
        )
        .join("")}
    </div>
    <div class="note-list dark-notes">
      ${venueLens.notes.map((note) => `<div class="note-item">${escapeHtml(note)}</div>`).join("")}
    </div>
  `;
}

function renderModelInfo(modelInfo) {
  const container = document.getElementById("model-credibility");
  container.innerHTML = `
    <div class="signal-header">
      <h3>${escapeHtml(modelInfo.headline)}</h3>
      <p>Compact credibility layer for how the outputs are built.</p>
    </div>
    <details class="credibility-drawer" open>
      <summary>Open model assumptions</summary>
      <div class="drawer-section">
        <h4>Simulation Flow</h4>
        <ul>
          ${modelInfo.steps.map((step) => `<li>${escapeHtml(step)}</li>`).join("")}
        </ul>
      </div>
      <div class="drawer-section">
        <h4>Assumptions</h4>
        <ul>
          ${modelInfo.assumptions.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
        </ul>
      </div>
    </details>
  `;
}

function renderChampionOdds(rows) {
  const maxProbability = Math.max(...rows.map((row) => row.probability), 0.001);
  const container = document.getElementById("champion-odds");
  container.innerHTML = rows
    .slice(0, 16)
    .map(
      (row) => `
        <div class="odds-row">
          <div class="odds-label">${renderTeamButton(row, `Group ${row.group} | FIFA #${row.fifaRank}`, "team-button")}</div>
          <div class="odds-track">
            <div class="odds-fill" style="width:${(row.probability / maxProbability) * 100}%"></div>
          </div>
          <div class="odds-value">${formatPercent(row.probability)}</div>
        </div>
      `
    )
    .join("");
}

function renderGroupOutlook(groups) {
  const container = document.getElementById("group-outlook");
  container.innerHTML = groups
    .map(
      (group) => `
        <article class="group-card">
          <div class="group-card-header">
            <div>
              <h3>Group ${group.group}</h3>
              <p>${escapeHtml(group.venue.city)}, ${escapeHtml(group.venue.country)} | ${escapeHtml(group.venue.climate)} | ${group.venue.altitudeM}m</p>
            </div>
            <div class="group-stat-badge">
              <span>Volatility</span>
              <strong>${group.volatilityIndex.toFixed(3)}</strong>
            </div>
          </div>
          <div class="group-subnote">
            Most likely table repeats ${formatPercent(group.mostLikelyTableProbability)} of runs.
          </div>
          <div class="group-likely-table">
            ${group.mostLikelyTable
              .map(
                (team, index) => `
                  <div class="likely-slot">
                    <span>${index + 1}</span>
                    <strong>${escapeHtml(team.name)}</strong>
                  </div>
                `
              )
              .join("")}
          </div>
          <div class="group-table">
            <div class="group-table-head">
              <span>Expected Table</span>
              <span>Adv</span>
              <span>Pts</span>
            </div>
            ${group.teams
              .map(
                (team) => `
                  <div class="group-row">
                    <div>
                      ${renderTeamButton(team, `Exp ${team.expectedFinish.toFixed(2)} | GF ${team.avgGF.toFixed(2)} | GA ${team.avgGA.toFixed(2)}`, "team-button")}
                    </div>
                    <div class="group-number">${formatPercent(team.advanceProbability)}</div>
                    <div class="group-number">${team.avgPoints.toFixed(2)}</div>
                  </div>
                `
              )
              .join("")}
          </div>
        </article>
      `
    )
    .join("");
}

function renderBracket(sampleTournament) {
  const container = document.getElementById("sample-bracket");
  const champion = state.teamIndex[sampleTournament.champion]?.name || sampleTournament.champion;
  const runnerUp = state.teamIndex[sampleTournament.runner_up]?.name || sampleTournament.runner_up;
  setText(
    "sample-summary",
    `${champion} beat ${runnerUp} in the current sample run and lifted the trophy in ${sampleTournament.finalVenue.city}.`
  );

  document.getElementById("sample-callout").innerHTML = `
    <div class="sample-hero-card">
      <div>
        <span class="metric-label">Sample champion</span>
        <strong>${escapeHtml(champion)}</strong>
        <p>${escapeHtml(sampleTournament.finalVenue.city)}, ${escapeHtml(sampleTournament.finalVenue.country)} | ${escapeHtml(sampleTournament.finalVenue.climate)}</p>
      </div>
      <div>
        <span class="metric-label">Runner-up</span>
        <strong>${escapeHtml(runnerUp)}</strong>
        <p>Final score: ${escapeHtml(sampleTournament.rounds[sampleTournament.rounds.length - 1].matches[0].scoreline)}</p>
      </div>
      <div>
        <span class="metric-label">Best 3rd Place Cut</span>
        <strong>${sampleTournament.thirdPlaceTable.filter((team) => team.qualified).length} teams</strong>
        <p>${sampleTournament.thirdPlaceTable.filter((team) => team.qualified).map((team) => escapeHtml(team.code)).join(" | ")}</p>
      </div>
    </div>
  `;

  container.innerHTML = sampleTournament.rounds
    .map(
      (round) => `
        <section class="bracket-round">
          <div class="bracket-round-header">
            <h3>${escapeHtml(round.round)}</h3>
            <span>${round.matches.length} matches</span>
          </div>
          ${round.matches
            .map((match) => {
              const homeTeam = getTeam(match.homeCode) || {
                code: match.homeCode,
                name: match.homeName,
                confederation: "UEFA",
                flagCode: "",
              };
              const awayTeam = getTeam(match.awayCode) || {
                code: match.awayCode,
                name: match.awayName,
                confederation: "UEFA",
                flagCode: "",
              };
              return `
                <div class="bracket-match ${match.winner ? "has-winner" : ""}">
                  <div class="match-line ${match.winner === match.homeCode ? "winner" : ""}">
                    ${renderTeamButton(homeTeam, "", "team-button match-team-button")}
                    <strong>${match.homeGoals}</strong>
                  </div>
                  <div class="match-line ${match.winner === match.awayCode ? "winner" : ""}">
                    ${renderTeamButton(awayTeam, "", "team-button match-team-button")}
                    <strong>${match.awayGoals}</strong>
                  </div>
                  <div class="match-meta">
                    <span>${escapeHtml(match.venue.city)}, ${escapeHtml(match.venue.country)}</span>
                    <span>${escapeHtml(match.scoreline)}</span>
                  </div>
                </div>
              `;
            })
            .join("")}
        </section>
      `
    )
    .join("");

  renderFeaturedPath(sampleTournament.featuredPath || []);
}

function renderFeaturedPath(path) {
  const container = document.getElementById("featured-path");
  if (!path.length) {
    container.innerHTML = "<div class=\"empty-state\">Run a simulation to see the selected team's path.</div>";
    return;
  }

  container.innerHTML = path
    .map(
      (entry) => `
        <div class="path-row">
          <div class="path-stage">${escapeHtml(entry.stage)}</div>
          <div class="path-body">
            <strong>${escapeHtml(entry.opponent)}</strong>
            <span>${escapeHtml(entry.scoreline)} | ${escapeHtml(entry.result)} | ${escapeHtml(entry.venueLabel)}</span>
          </div>
        </div>
      `
    )
    .join("");
}

function renderTeamTable(rows) {
  const body = document.getElementById("team-table");
  body.innerHTML = rows
    .map(
      (row) => `
        <tr>
          <td>${renderTeamButton(row, "", "team-button table-team-button")}</td>
          <td>${row.group}</td>
          <td>${row.fifaRank}</td>
          <td>${row.power.toFixed(1)}</td>
          <td class="cell-probability">${formatPercent(row.advanceProbability)}</td>
          <td class="cell-probability">${formatPercent(row.quarterfinalProbability)}</td>
          <td class="cell-probability">${formatPercent(row.championProbability)}</td>
          <td>${row.expectedFinish.toFixed(2)}</td>
          <td>${row.avgGoalsFor.toFixed(2)}</td>
          <td>${row.avgGoalsAgainst.toFixed(2)}</td>
          <td>${row.avgTravelLoad.toFixed(3)}</td>
        </tr>
      `
    )
    .join("");
}

function openTeamModal(code) {
  const profile = state.teamProfiles[code];
  if (!profile) {
    return;
  }

  modalContent.innerHTML = `
    <div class="modal-header">
      ${renderTeamIdentity(profile, `Group ${profile.group} | FIFA #${profile.fifaRank}`)}
      <div class="modal-header-copy">
        <h2 id="team-modal-title">${escapeHtml(profile.name)}</h2>
        <p>${escapeHtml(profile.style)} | ${escapeHtml(profile.confederation)} | Power ${profile.power.toFixed(1)}</p>
      </div>
    </div>
    <div class="modal-metrics">
      <div class="feature-metric"><span>Advance</span><strong>${formatPercent(profile.advanceProbability)}</strong></div>
      <div class="feature-metric"><span>Round of 16</span><strong>${formatPercent(profile.roundOf16Probability)}</strong></div>
      <div class="feature-metric"><span>Quarterfinal</span><strong>${formatPercent(profile.quarterfinalProbability)}</strong></div>
      <div class="feature-metric"><span>Title</span><strong>${formatPercent(profile.championProbability)}</strong></div>
      <div class="feature-metric"><span>GF</span><strong>${profile.avgGoalsFor.toFixed(2)}</strong></div>
      <div class="feature-metric"><span>GA</span><strong>${profile.avgGoalsAgainst.toFixed(2)}</strong></div>
      <div class="feature-metric"><span>Travel</span><strong>${profile.avgTravelLoad.toFixed(3)}</strong></div>
      <div class="feature-metric"><span>Venue Edge</span><strong>${formatSigned(profile.avgVenueEdge)}</strong></div>
    </div>
    <div class="modal-grid">
      <div class="mini-panel">
        <h4>Power Breakdown</h4>
        ${renderBreakdownRows(profile.powerBreakdown)}
      </div>
      <div class="mini-stack">
        ${renderSimpleMetricList("Strengths", profile.strengths)}
        ${renderSimpleMetricList("Risks", profile.risks)}
      </div>
      <div class="mini-panel">
        <h4>Likely Knockout Opponents</h4>
        ${profile.commonOpponents
          .map(
            (item) => `
              <div class="mini-row">
                <span>${escapeHtml(item.stage)}</span>
                <strong>${escapeHtml(item.opponent)} ${formatPercent(item.probability)}</strong>
              </div>
            `
          )
          .join("")}
      </div>
    </div>
    <div class="modal-grid">
      <div class="mini-panel">
        <h4>Sample Tournament Path</h4>
        ${(profile.samplePath || [])
          .map(
            (entry) => `
              <div class="path-row compact">
                <div class="path-stage">${escapeHtml(entry.stage)}</div>
                <div class="path-body">
                  <strong>${escapeHtml(entry.opponent)}</strong>
                  <span>${escapeHtml(entry.scoreline)} | ${escapeHtml(entry.result)} | ${escapeHtml(entry.venueLabel)}</span>
                </div>
              </div>
            `
          )
          .join("")}
      </div>
      <div class="mini-panel">
        <h4>Scout Notes</h4>
        ${profile.notes.map((note) => `<div class="note-item">${escapeHtml(note)}</div>`).join("")}
      </div>
    </div>
  `;

  modalShell.hidden = false;
  document.body.classList.add("modal-open");
}

function closeTeamModal() {
  modalShell.hidden = true;
  document.body.classList.remove("modal-open");
}

async function copyShareSnapshot() {
  if (!state.latestSimulation?.shareCard) {
    return;
  }
  const text = state.latestSimulation.shareCard.lines.join("\n");
  try {
    await navigator.clipboard.writeText(text);
    setText("share-status", "Summary copied to clipboard.");
  } catch (_error) {
    setText("share-status", "Clipboard copy failed in this browser.");
  }
}

function downloadRunSnapshot() {
  if (!state.latestSimulation?.shareCard) {
    return;
  }
  const payload = JSON.stringify(state.latestSimulation, null, 2);
  const blob = new Blob([payload], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = state.latestSimulation.shareCard.downloadName || "world-cup-snapshot.json";
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
  setText("share-status", "Downloaded JSON snapshot.");
}

async function runSimulation() {
  buildStatus.textContent = "Running Monte Carlo tournament paths...";
  const payload = {
    iterations: Number(iterationsInput.value),
    scenario: state.scenario,
    featuredTeam: featuredTeamSelect.value,
    hostAdvantage: hostAdvantageInput.checked,
  };

  const response = await fetch("/api/simulate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    buildStatus.textContent = "Simulation failed.";
    return;
  }

  const data = await response.json();
  state.latestSimulation = data;
  state.teamProfiles = data.teamProfiles;
  buildStatus.textContent = "Ready.";
  setText(
    "summary-context",
    `${data.metadata.iterations} runs | ${data.metadata.scenario} scenario | host advantage ${data.metadata.hostAdvantage ? "on" : "off"} | run ${data.metadata.runId}`
  );

  renderSummary(data.summary);
  renderFeaturedTeam(data.featuredTeam);
  renderScenarioCompare(data.scenarioCompare);
  renderShareCard(data.shareCard);
  renderUpsetTracker(data.upsetTracker);
  renderVenueLens(data.venueLens);
  renderModelInfo(data.modelInfo);
  renderChampionOdds(data.championOdds);
  renderGroupOutlook(data.groupOutlook);
  renderBracket(data.sampleTournament);
  renderTeamTable(data.teamTable);
}

async function initialize() {
  const response = await fetch("/api/metadata");
  const metadata = await response.json();
  state.metadata = metadata;
  metadata.teams.forEach((team) => {
    state.teamIndex[team.code] = team;
  });

  renderHero(metadata);
  iterationsInput.value = metadata.defaults.iterations;
  iterationsOutput.textContent = metadata.defaults.iterations;
  state.scenario = metadata.defaults.scenario;
  setText("build-status", "Model loaded.");

  metadata.teams.forEach((team) => {
    const option = document.createElement("option");
    option.value = team.code;
    option.textContent = `${flagFromCode(team.flagCode)} ${team.name} | Group ${team.group} | FIFA #${team.fifaRank}`;
    if (team.code === metadata.defaults.featuredTeam) {
      option.selected = true;
    }
    featuredTeamSelect.appendChild(option);
  });

  await runSimulation();
}

initialize();
