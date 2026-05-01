const state = {
  metadata: null,
  teamIndex: {},
  teamProfiles: {},
  latestSimulation: null,
  scenario: "balanced",
  matrixSort: {
    column: "championProbability",
    direction: "desc",
  },
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
const runButton = form.querySelector('[type="submit"]');
const modalShell = document.getElementById("team-modal");
const modalContent = document.getElementById("team-modal-content");
const modalCloseButton = document.getElementById("team-modal-close");
const navLinks = Array.from(document.querySelectorAll(".nav-links a"));
const matrixHeaders = Array.from(document.querySelectorAll("#matrix-table thead th[data-sort]"));

iterationsInput.addEventListener("input", () => {
  iterationsOutput.textContent = iterationsInput.value;
});

document.querySelectorAll(".scenario-button").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".scenario-button").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    state.scenario = button.dataset.scenario;
  });
});

matrixHeaders.forEach((header) => {
  header.addEventListener("click", () => {
    const column = header.dataset.sort;
    if (!column) {
      return;
    }
    if (state.matrixSort.column === column) {
      state.matrixSort.direction = state.matrixSort.direction === "asc" ? "desc" : "asc";
    } else {
      state.matrixSort.column = column;
      state.matrixSort.direction = defaultSortDirection(column);
    }
    if (state.latestSimulation) {
      renderTeamTable(state.latestSimulation.teamTable);
    }
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
    const code = teamTrigger.dataset.teamCode;
    if (code) {
      openTeamModal(code);
    }
    return;
  }

  const shareTrigger = target.closest("[data-share-action]");
  if (shareTrigger instanceof HTMLElement) {
    if (shareTrigger.dataset.shareAction === "copy") {
      await copyShareSnapshot();
    }
    if (shareTrigger.dataset.shareAction === "download") {
      downloadRunSnapshot();
    }
  }
});

function formatPercent(value) {
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function formatSigned(value, decimals = 3) {
  const number = Number(value);
  return `${number >= 0 ? "+" : ""}${number.toFixed(decimals)}`;
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
    return String.fromCodePoint(0x1f3f4, 0xe0067, 0xe0062, 0xe0065, 0xe006e, 0xe0067, 0xe007f);
  }
  if (code === "gb-sct") {
    return String.fromCodePoint(0x1f3f4, 0xe0067, 0xe0062, 0xe0073, 0xe0063, 0xe0074, 0xe007f);
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

function defaultSortDirection(column) {
  if (["name", "group", "fifaRank", "expectedFinish", "avgGoalsAgainst", "avgTravelLoad"].includes(column)) {
    return "asc";
  }
  return "desc";
}

function setText(id, value) {
  const element = document.getElementById(id);
  if (element) {
    element.textContent = value;
  }
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
        <span class="team-meta">${escapeHtml(team.code)} | ${escapeHtml(team.confederation)}${metaText ? ` | ${escapeHtml(metaText)}` : ""}</span>
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
  const labels = [
    metadata.format,
    metadata.dates,
    `${metadata.teams.length} qualified teams`,
    `${metadata.groups.length} groups`,
    `FIFA rank snapshot ${metadata.rankingDate}`,
  ];
  chips.innerHTML = labels
    .map((label) => `<span class="fact-chip">${escapeHtml(label)}</span>`)
    .join("");
}

function renderSummary(summary) {
  const grid = document.getElementById("summary-grid");
  const cards = [
    {
      label: "Favorite",
      value: summary.favorite.name,
      subtext: `FIFA #${summary.favorite.fifaRank} · ${formatPercent(summary.favorite.probability)} title`,
    },
    {
      label: "Dark Horse",
      value: summary.darkHorse.name,
      subtext: `FIFA #${summary.darkHorse.fifaRank} · ${formatPercent(summary.darkHorse.probability)} title`,
    },
    {
      label: "Goals / Match",
      value: summary.averageGoalsPerMatch.toFixed(2),
      subtext: "Average across the simulation slate",
    },
    {
      label: "Upset Rate",
      value: formatPercent(summary.upsetRate),
      subtext: "Lower-rated side wins",
    },
  ];

  grid.innerHTML = cards
    .map(
      (card) => `
        <div class="stat-cell">
          <div class="stat-label">${escapeHtml(card.label)}</div>
          <div class="stat-val">${escapeHtml(card.value)}</div>
          <div class="stat-sub">${escapeHtml(card.subtext)}</div>
        </div>
      `
    )
    .join("");
}

function renderBreakdownRows(items) {
  const maxContribution = Math.max(...items.map((item) => Number(item.contribution)), 0.01);
  return items
    .map(
      (item) => `
        <div class="breakdown-row">
          <div class="breakdown-row-top">
            <span>${escapeHtml(item.label)}</span>
            <strong>${Number(item.contribution).toFixed(2)}</strong>
          </div>
          <div class="breakdown-track">
            <div class="breakdown-fill" style="width:${(Number(item.contribution) / maxContribution) * 100}%"></div>
          </div>
        </div>
      `
    )
    .join("");
}

function renderSimpleMetricList(title, items, kind = "value") {
  return `
    <div class="panel-card">
      <div class="mini-head">
        <h3>${escapeHtml(title)}</h3>
      </div>
      <div class="mini-stack">
        ${items
          .map((item) => {
            const label = item.label || item.stage || item.opponent;
            const value = kind === "percent" ? formatPercent(item.probability) : Number(item.value).toFixed(1);
            return `
              <div class="mini-row">
                <span>${escapeHtml(label)}</span>
                <strong>${escapeHtml(value)}</strong>
              </div>
            `;
          })
          .join("")}
      </div>
    </div>
  `;
}

function renderFeaturedTeam(featuredTeam) {
  setText("featured-heading", `Group ${featuredTeam.group} · FIFA #${featuredTeam.fifaRank} · ${featuredTeam.style}`);

  const container = document.getElementById("featured-team-card");
  container.innerHTML = `
    <div class="featured-topline">
      ${renderTeamButton(featuredTeam, `Group ${featuredTeam.group} | FIFA #${featuredTeam.fifaRank}`)}
      <button type="button" class="mini-button" data-team-code="${escapeHtml(featuredTeam.code)}">Open Team Page</button>
    </div>
    <div class="featured-tags">
      <span class="mini-tag">Anchor ${featuredTeam.rankingAnchor.toFixed(1)}</span>
      <span class="mini-tag">Power ${featuredTeam.power.toFixed(1)}</span>
      <span class="mini-tag">${escapeHtml(featuredTeam.style)}</span>
      <span class="mini-tag">${escapeHtml(featuredTeam.confederation)}</span>
    </div>
    <div class="featured-metrics">
      <div class="feature-metric">
        <span>Advance</span>
        <strong>${formatPercent(featuredTeam.advanceProbability)}</strong>
      </div>
      <div class="feature-metric">
        <span>Quarterfinal</span>
        <strong>${formatPercent(featuredTeam.quarterfinalProbability)}</strong>
      </div>
      <div class="feature-metric">
        <span>Win</span>
        <strong>${formatPercent(featuredTeam.championProbability)}</strong>
      </div>
      <div class="feature-metric">
        <span>Avg Pts</span>
        <strong>${featuredTeam.avgGroupPoints.toFixed(2)}</strong>
      </div>
    </div>
    <div class="featured-lower">
      <div class="panel-card">
        <div class="mini-head">
          <h3>Why This Team?</h3>
        </div>
        <div class="breakdown-grid">${renderBreakdownRows(featuredTeam.powerBreakdown)}</div>
      </div>
      ${renderSimpleMetricList("Strengths", featuredTeam.strengths)}
      ${renderSimpleMetricList(
        "Likely KO Opponents",
        featuredTeam.commonOpponents.map((item) => ({
          label: `${item.stage}: ${item.opponent}`,
          probability: item.probability,
        })),
        "percent"
      )}
    </div>
  `;

  const notes = document.getElementById("model-notes");
  notes.innerHTML = featuredTeam.notes.map((note) => `<div class="note-item">${escapeHtml(note)}</div>`).join("");
}

function renderScenarioCompare(rows) {
  const container = document.getElementById("scenario-compare");
  container.innerHTML = rows
    .map(
      (row) => `
        <article class="scenario-card ${row.active ? "active" : ""}">
          <div class="scenario-card-top">
            <span class="scenario-label">${escapeHtml(row.label)}</span>
            ${row.active ? '<span class="current-tag">Current</span>' : ""}
          </div>
          <div class="scenario-value">${formatPercent(row.titleProbability)}</div>
          <div class="scenario-sub">${escapeHtml(row.featuredTeam)} title odds</div>
          <div class="scenario-mini">
            <div><span>Advance</span><strong>${formatPercent(row.advanceProbability)}</strong></div>
            <div><span>Semifinal</span><strong>${formatPercent(row.semifinalProbability)}</strong></div>
            <div><span>Goals / Match</span><strong>${row.averageGoalsPerMatch.toFixed(2)}</strong></div>
            <div><span>Upset Rate</span><strong>${formatPercent(row.upsetRate)}</strong></div>
          </div>
          <div class="scenario-footer">Favorite: ${escapeHtml(row.fieldFavorite)} (${formatPercent(row.favoriteProbability)})</div>
        </article>
      `
    )
    .join("");
}

function renderShareCard(shareCard) {
  const container = document.getElementById("share-card");
  container.innerHTML = `
    <div class="share-lines">
      <div class="share-status" id="share-status">Ready to copy or download.</div>
      ${shareCard.lines.map((line) => `<div class="share-line">${escapeHtml(line)}</div>`).join("")}
    </div>
    <div class="share-actions">
      <button type="button" class="mini-button" data-share-action="copy">Copy Summary</button>
      <button type="button" class="mini-button" data-share-action="download">Download JSON</button>
    </div>
  `;
}

function renderUpsetTracker(upsetTracker) {
  const biggest = upsetTracker.biggestUpsetCandidate;
  const container = document.getElementById("upset-tracker");
  container.innerHTML = `
    <div class="signal-head">
      <h3>Upset Tracker</h3>
      <p>Where the bracket feels fragile.</p>
    </div>
    <div class="signal-stack">
      <div class="signal-row">
        <span>Biggest Upset Candidate</span>
        <strong>${biggest ? `${escapeHtml(biggest.winner)} over ${escapeHtml(biggest.loser)}` : "No signal yet"}</strong>
        ${biggest ? `<small>${escapeHtml(biggest.stage)} · ${formatPercent(biggest.probability)} · ${biggest.powerGap.toFixed(1)} power gap</small>` : ""}
      </div>
      <div class="signal-row">
        <span>Most Volatile Group</span>
        <strong>Group ${escapeHtml(upsetTracker.mostVolatileGroup.group)}</strong>
        <small>Volatility ${upsetTracker.mostVolatileGroup.volatilityIndex.toFixed(3)} · table repeat ${formatPercent(upsetTracker.mostVolatileGroup.mostLikelyTableProbability)}</small>
      </div>
      <div class="signal-row">
        <span>Fragile Favorite</span>
        <strong>${escapeHtml(upsetTracker.fragileFavorite.name)}</strong>
        <small>Advance ${formatPercent(upsetTracker.fragileFavorite.advanceProbability)} · QF ${formatPercent(upsetTracker.fragileFavorite.quarterfinalProbability)} · Win ${formatPercent(upsetTracker.fragileFavorite.championProbability)}</small>
      </div>
    </div>
  `;
}

function renderVenueLens(venueLens) {
  const container = document.getElementById("venue-lens");
  container.innerHTML = `
    <div class="signal-head">
      <h3>Venue + Travel</h3>
      <p>${escapeHtml(venueLens.headline)}</p>
    </div>
    <div class="signal-stack">
      ${venueLens.cards
        .map(
          (card) => `
            <div class="venue-chip">
              <span>${escapeHtml(card.label)}</span>
              <strong>${escapeHtml(card.value)}</strong>
              <small>${escapeHtml(card.detail)}</small>
            </div>
          `
        )
        .join("")}
    </div>
  `;
}

function renderModelInfo(modelInfo) {
  const container = document.getElementById("model-credibility");
  container.innerHTML = `
    <div class="signal-head">
      <h3>${escapeHtml(modelInfo.headline)}</h3>
      <p>Compact credibility layer for the model.</p>
    </div>
    <details open>
      <summary>Open Model Assumptions</summary>
      <div class="drawer-copy">
        <strong>Simulation flow</strong>
        <ul>${modelInfo.steps.map((step) => `<li>${escapeHtml(step)}</li>`).join("")}</ul>
        <strong>Assumptions</strong>
        <ul>${modelInfo.assumptions.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
      </div>
    </details>
  `;
}

function renderChampionOdds(rows) {
  const container = document.getElementById("champion-odds");
  const maxProbability = Math.max(...rows.map((row) => Number(row.probability)), 0.001);
  container.innerHTML = rows
    .slice(0, 16)
    .map(
      (row, index) => `
        <div class="odds-row">
          <div class="odds-rank">${index + 1}</div>
          <div class="odds-label">${renderTeamButton(row, `Group ${row.group} | FIFA #${row.fifaRank}`)}</div>
          <div class="odds-bar-wrap">
            <div class="odds-bar" style="width:${(Number(row.probability) / maxProbability) * 100}%"></div>
          </div>
          <div class="odds-pct">${formatPercent(row.probability)}</div>
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
          <div class="group-head">
            <div class="group-letter">Group ${escapeHtml(group.group)}</div>
            <div class="group-meta">Avg power ${group.averagePower.toFixed(1)}<br>Vol ${group.volatilityIndex.toFixed(3)}</div>
          </div>
          <div class="group-note">${escapeHtml(group.venue.city)}, ${escapeHtml(group.venue.country)} · ${escapeHtml(group.venue.climate)} · most likely table ${formatPercent(group.mostLikelyTableProbability)}</div>
          ${group.teams
            .map(
              (team) => `
                <div class="group-row">
                  <div>${renderTeamButton(team, `FIFA #${team.fifaRank} | Exp ${team.expectedFinish.toFixed(2)}`)}</div>
                  <div class="group-adv">${formatPercent(team.advanceProbability)}</div>
                  <div class="group-pts">${team.avgPoints.toFixed(2)}</div>
                </div>
              `
            )
            .join("")}
        </article>
      `
    )
    .join("");
}

function renderBracket(sampleTournament) {
  const container = document.getElementById("sample-bracket");
  const champion = state.teamIndex[sampleTournament.champion]?.name || sampleTournament.champion;
  const runnerUp = state.teamIndex[sampleTournament.runner_up]?.name || sampleTournament.runner_up;
  const finalMatch = sampleTournament.rounds[sampleTournament.rounds.length - 1].matches[0];

  setText("sample-summary", `${champion} beat ${runnerUp} in this sample run and lifted the trophy in ${sampleTournament.finalVenue.city}.`);

  document.getElementById("sample-callout").innerHTML = `
    <div class="sample-info">
      <span class="sample-label">Sample Champion</span>
      <strong>${escapeHtml(champion)}</strong>
      <p>${escapeHtml(sampleTournament.finalVenue.city)}, ${escapeHtml(sampleTournament.finalVenue.country)} · ${escapeHtml(sampleTournament.finalVenue.climate)}</p>
    </div>
    <div class="sample-info">
      <span class="sample-label">Runner-Up</span>
      <strong>${escapeHtml(runnerUp)}</strong>
      <p>Final score: ${escapeHtml(finalMatch.scoreline)}</p>
    </div>
    <div class="sample-info">
      <span class="sample-label">Best 3rd Place Cut</span>
      <strong>${sampleTournament.thirdPlaceTable.filter((team) => team.qualified).length} teams</strong>
      <p>${sampleTournament.thirdPlaceTable.filter((team) => team.qualified).map((team) => escapeHtml(team.code)).join(" · ")}</p>
    </div>
  `;

  container.innerHTML = sampleTournament.rounds
    .map((round, index) => {
      const finalColumn = index === sampleTournament.rounds.length - 1;
      return `
        <div class="round">
          <div class="round-label">${escapeHtml(round.round)}</div>
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
                <div class="match ${finalColumn ? "final-match" : ""}">
                  <div class="match-team ${match.winner === match.homeCode ? "winner" : ""}">
                    ${renderTeamButton(homeTeam, "", "team-button")}
                    <div class="match-score">${match.homeGoals}</div>
                  </div>
                  <div class="match-team ${match.winner === match.awayCode ? "winner" : ""}">
                    ${renderTeamButton(awayTeam, "", "team-button")}
                    <div class="match-score">${match.awayGoals}</div>
                  </div>
                  <div class="match-winner-tag">${escapeHtml(match.venue.city)} · ${escapeHtml(match.scoreline)}</div>
                </div>
              `;
            })
            .join("")}
          ${finalColumn ? `<div class="champion-badge">Sample Champion<span class="champion-name">${escapeHtml(champion)}</span></div>` : ""}
        </div>
      `;
    })
    .join("");

  renderFeaturedPath(sampleTournament.featuredPath || []);
}

function renderFeaturedPath(path) {
  const container = document.getElementById("featured-path");
  if (!path.length) {
    container.innerHTML = `<div class="share-status">Run a simulation to see the selected team's path.</div>`;
    return;
  }

  container.innerHTML = path
    .map(
      (entry) => `
        <div class="path-row">
          <div class="path-stage">${escapeHtml(entry.stage)}</div>
          <div class="path-body">
            <strong>${escapeHtml(entry.opponent)}</strong>
            <span>${escapeHtml(entry.scoreline)} · ${escapeHtml(entry.result)} · ${escapeHtml(entry.venueLabel)}</span>
          </div>
        </div>
      `
    )
    .join("");
}

function probabilityCell(value, fillClass, highlight = false) {
  return `
    <div class="prob-cell">
      <div class="pct-b"><div class="pct-f ${fillClass}" style="width:${Math.min(Number(value) * 100, 100)}%"></div></div>
      <span class="pct-n ${highlight ? "win-n" : ""}">${formatPercent(value)}</span>
    </div>
  `;
}

function sortMatrixRows(rows) {
  const direction = state.matrixSort.direction === "asc" ? 1 : -1;
  const column = state.matrixSort.column;
  const sorted = [...rows];
  sorted.sort((left, right) => {
    const leftValue = left[column];
    const rightValue = right[column];
    if (typeof leftValue === "string" || typeof rightValue === "string") {
      return String(leftValue).localeCompare(String(rightValue)) * direction;
    }
    return (Number(leftValue) - Number(rightValue)) * direction;
  });
  return sorted;
}

function renderMatrixHeaders() {
  matrixHeaders.forEach((header) => {
    const active = header.dataset.sort === state.matrixSort.column;
    header.classList.toggle("active", active);
    const label = header.textContent.replace(/[↑↓]/g, "").trim();
    header.innerHTML = `${escapeHtml(label)}${active ? `<span class="sort-arrow">${state.matrixSort.direction === "asc" ? "↑" : "↓"}</span>` : ""}`;
  });
}

function renderTeamTable(rows) {
  const body = document.getElementById("team-table");
  const sortedRows = sortMatrixRows(rows);
  renderMatrixHeaders();
  body.innerHTML = sortedRows
    .map(
      (row) => `
        <tr>
          <td class="table-team">${renderTeamButton(row, "", "team-button")}</td>
          <td class="num">${row.fifaRank}</td>
          <td class="num"><span class="grp-b">${escapeHtml(row.group)}</span></td>
          <td class="num"><span class="pow-v">${row.power.toFixed(1)}</span></td>
          <td class="num">${probabilityCell(row.advanceProbability, "f-adv")}</td>
          <td class="num">${probabilityCell(row.quarterfinalProbability, "f-qf")}</td>
          <td class="num">${probabilityCell(row.semifinalProbability, "f-sf")}</td>
          <td class="num">${probabilityCell(row.championProbability, "f-win", true)}</td>
          <td class="num"><span class="pts-v">${row.avgGroupPoints.toFixed(2)}</span></td>
          <td class="num">${row.expectedFinish.toFixed(2)}</td>
          <td class="num">${row.avgGoalsFor.toFixed(2)}</td>
          <td class="num">${row.avgGoalsAgainst.toFixed(2)}</td>
          <td class="num">${row.avgTravelLoad.toFixed(3)}</td>
        </tr>
      `
    )
    .join("");
}

function renderTeamModalList(title, items, kind = "value") {
  return `
    <div class="panel-card">
      <div class="mini-head"><h3>${escapeHtml(title)}</h3></div>
      <div class="mini-stack">
        ${items
          .map((item) => {
            const label = item.label || item.stage || item.opponent;
            const value = kind === "percent" ? formatPercent(item.probability) : Number(item.value).toFixed(1);
            return `
              <div class="mini-row">
                <span>${escapeHtml(label)}</span>
                <strong>${escapeHtml(value)}</strong>
              </div>
            `;
          })
          .join("")}
      </div>
    </div>
  `;
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
        <p>${escapeHtml(profile.style)} · ${escapeHtml(profile.confederation)} · Power ${profile.power.toFixed(1)} · travel ${profile.avgTravelLoad.toFixed(3)} · venue edge ${formatSigned(profile.avgVenueEdge)}</p>
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
      <div class="panel-card">
        <div class="mini-head"><h3>Power Breakdown</h3></div>
        <div class="breakdown-grid">${renderBreakdownRows(profile.powerBreakdown)}</div>
      </div>
      ${renderTeamModalList("Strengths", profile.strengths)}
      ${renderTeamModalList("Risks", profile.risks)}
    </div>
    <div class="modal-grid">
      ${renderTeamModalList(
        "Likely Knockout Opponents",
        profile.commonOpponents.map((item) => ({
          label: `${item.stage}: ${item.opponent}`,
          probability: item.probability,
        })),
        "percent"
      )}
      <div class="panel-card">
        <div class="mini-head"><h3>Sample Tournament Path</h3></div>
        ${(profile.samplePath || [])
          .map(
            (entry) => `
              <div class="path-row">
                <div class="path-stage">${escapeHtml(entry.stage)}</div>
                <div class="path-body">
                  <strong>${escapeHtml(entry.opponent)}</strong>
                  <span>${escapeHtml(entry.scoreline)} · ${escapeHtml(entry.result)} · ${escapeHtml(entry.venueLabel)}</span>
                </div>
              </div>
            `
          )
          .join("")}
      </div>
      <div class="panel-card">
        <div class="mini-head"><h3>Scout Notes</h3></div>
        <div class="note-stack">${profile.notes.map((note) => `<div class="note-item">${escapeHtml(note)}</div>`).join("")}</div>
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

function updateNavMeta(data) {
  const navMeta = document.getElementById("nav-meta");
  navMeta.textContent = `${data.metadata.iterations} runs · ${data.metadata.scenario} · host adv ${data.metadata.hostAdvantage ? "on" : "off"} · FIFA ${state.metadata.rankingDate}`;
}

function activateNavLink(hash) {
  navLinks.forEach((link) => {
    link.classList.toggle("active", link.getAttribute("href") === hash);
  });
}

function setupSectionObserver() {
  const sections = ["#hero", "#odds", "#groups", "#bracket", "#matrix"]
    .map((selector) => document.querySelector(selector))
    .filter(Boolean);

  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((left, right) => right.intersectionRatio - left.intersectionRatio)[0];
      if (visible?.target?.id) {
        activateNavLink(`#${visible.target.id}`);
      }
    },
    {
      threshold: [0.2, 0.45, 0.7],
      rootMargin: "-64px 0px -40% 0px",
    }
  );

  sections.forEach((section) => observer.observe(section));
}

async function runSimulation() {
  buildStatus.textContent = "Running Monte Carlo tournament paths...";
  runButton.textContent = "Running…";
  runButton.disabled = true;

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
    runButton.textContent = "Run Simulation";
    runButton.disabled = false;
    return;
  }

  const data = await response.json();
  state.latestSimulation = data;
  state.teamProfiles = data.teamProfiles;

  buildStatus.textContent = "Ready.";
  runButton.textContent = "Run Simulation";
  runButton.disabled = false;

  setText(
    "summary-context",
    `${data.metadata.iterations} runs · ${data.metadata.scenario} · host advantage ${data.metadata.hostAdvantage ? "on" : "off"} · run ${data.metadata.runId}`
  );
  updateNavMeta(data);

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

  metadata.teams.forEach((team) => {
    const option = document.createElement("option");
    option.value = team.code;
    option.textContent = `${flagFromCode(team.flagCode)} ${team.name} | Group ${team.group} | FIFA #${team.fifaRank}`;
    if (team.code === metadata.defaults.featuredTeam) {
      option.selected = true;
    }
    featuredTeamSelect.appendChild(option);
  });

  setupSectionObserver();
  await runSimulation();
}

initialize();
