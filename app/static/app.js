const state = {
  metadata: null,
  teamIndex: {},
  scenario: "balanced",
};

const CONFED_ASSETS = {
  UEFA: {
    name: "UEFA",
    url: "/static/assets/federations/uefa.svg",
  },
  CONMEBOL: {
    name: "CONMEBOL",
    url: "/static/assets/federations/conmebol.svg",
  },
  Concacaf: {
    name: "Concacaf",
    url: "/static/assets/federations/concacaf.svg",
  },
  AFC: {
    name: "AFC",
    url: "/static/assets/federations/afc.svg",
  },
  CAF: {
    name: "CAF",
    url: "/static/assets/federations/caf.svg",
  },
  OFC: {
    name: "OFC",
    url: "/static/assets/federations/ofc.svg",
  },
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

const SPECIAL_FLAG_ASSETS = {
  "gb-eng": "https://commons.wikimedia.org/wiki/Special:FilePath/Flag%20of%20England.svg",
  "gb-sct": "https://commons.wikimedia.org/wiki/Special:FilePath/Flag%20of%20Scotland.svg",
};

const form = document.getElementById("simulation-form");
const iterationsInput = document.getElementById("iterations");
const iterationsOutput = document.getElementById("iterations-output");
const featuredTeamSelect = document.getElementById("featured-team");
const hostAdvantageInput = document.getElementById("host-advantage");
const buildStatus = document.getElementById("build-status");

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

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  await runSimulation();
});

function formatPercent(value) {
  return `${(value * 100).toFixed(1)}%`;
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
  if (SPECIAL_FLAG_ASSETS[code]) {
    return SPECIAL_FLAG_ASSETS[code];
  }
  return `https://flagcdn.com/w80/${code.toLowerCase()}.png`;
}

function teamBadgeUrl(team) {
  return TEAM_BADGE_ASSETS[team.code] || "";
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
          alt="${team.name} badge"
          loading="lazy"
          referrerpolicy="no-referrer"
          onerror="if(this.dataset.fallback && this.src !== this.dataset.fallback){this.src=this.dataset.fallback;this.dataset.fallback='';}else{this.style.display='none';}"
        >
        <img
          class="team-flag-img"
          src="${flagAssetUrl(team.flagCode)}"
          alt="${team.name} flag"
          loading="lazy"
          referrerpolicy="no-referrer"
          onerror="this.replaceWith(Object.assign(document.createElement('span'), {className:'team-flag-fallback', textContent:'${flagFromCode(team.flagCode)}'}))"
        >
      </div>
      <div class="team-text">
        <strong>${team.name}</strong>
        <span class="team-meta">
          ${team.code} | ${team.confederation}${metaText ? ` | ${metaText}` : ""}
        </span>
      </div>
    </div>
  `;
}

function renderMatchTeam(code, label, goals) {
  const team = state.teamIndex[code] || { code, name: label, confederation: "UEFA", flagCode: "" };
  return `
    <div class="match-line">
      ${renderTeamIdentity(team)}
      <strong>${goals}</strong>
    </div>
  `;
}

function setText(id, value) {
  const element = document.getElementById(id);
  if (element) {
    element.textContent = value;
  }
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
      subtext: "Average output across the simulated tournament slate.",
    },
    {
      label: "Upset Rate",
      value: formatPercent(summary.upsetRate),
      subtext: "Share of matches won by the lower-rated side.",
    },
  ];

  grid.innerHTML = cards
    .map(
      (card) => `
        <article class="metric-card">
          <div class="metric-label">${card.label}</div>
          <div class="metric-value">${card.value}</div>
          <div class="metric-subtext">${card.subtext}</div>
        </article>
      `
    )
    .join("");
}

function renderFeaturedTeam(featuredTeam) {
  setText("featured-heading", `Group ${featuredTeam.group} | FIFA #${featuredTeam.fifaRank}`);
  const container = document.getElementById("featured-team-card");
  container.innerHTML = `
    ${renderTeamIdentity(featuredTeam)}
    <div class="featured-meta">
      <span class="meta-pill">FIFA #${featuredTeam.fifaRank}</span>
      <span class="meta-pill">Anchor ${featuredTeam.rankingAnchor.toFixed(1)}</span>
      <span class="meta-pill">Power ${featuredTeam.power.toFixed(1)}</span>
      <span class="meta-pill">${featuredTeam.style}</span>
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
  `;

  const notes = document.getElementById("model-notes");
  notes.innerHTML = featuredTeam.notes
    .map((note) => `<div class="note-item">${note}</div>`)
    .join("");
}

function renderChampionOdds(rows) {
  const maxProbability = Math.max(...rows.map((row) => row.probability), 0.001);
  const container = document.getElementById("champion-odds");
  container.innerHTML = rows
    .slice(0, 14)
    .map((row) => `
      <div class="odds-row">
        <div class="odds-label">${renderTeamIdentity(row, `Group ${row.group} | FIFA #${row.fifaRank}`)}</div>
        <div class="odds-track">
          <div class="odds-fill" style="width:${(row.probability / maxProbability) * 100}%"></div>
        </div>
        <div class="odds-value">${formatPercent(row.probability)}</div>
      </div>
    `)
    .join("");
}

function renderGroupOutlook(groups) {
  const container = document.getElementById("group-outlook");
  container.innerHTML = groups
    .map((group) => `
      <article class="group-card">
        <h3>Group ${group.group}</h3>
        <p>Average power ${group.averagePower.toFixed(1)}</p>
        ${group.teams
          .map(
            (team) => `
              <div class="group-row">
                <div>${renderTeamIdentity(team, `FIFA #${team.fifaRank} | Win group ${formatPercent(team.groupWinProbability)}`)}</div>
                <div class="group-number">${formatPercent(team.advanceProbability)}</div>
                <div class="group-number">${team.avgPoints.toFixed(2)} pts</div>
              </div>
            `
          )
          .join("")}
      </article>
    `)
    .join("");
}

function renderBracket(sampleTournament) {
  const container = document.getElementById("sample-bracket");
  const champion = state.teamIndex[sampleTournament.champion]?.name || sampleTournament.champion;
  const runnerUp = state.teamIndex[sampleTournament.runner_up]?.name || sampleTournament.runner_up;
  setText("sample-summary", `${champion} beat ${runnerUp} in the current sample path.`);

  container.innerHTML = sampleTournament.rounds
    .map(
      (round) => `
        <section class="bracket-round">
          <h3>${round.round}</h3>
          ${round.matches
            .map((match) => {
              const winnerName = state.teamIndex[match.winner]?.name || match.winner;
              return `
                <div class="bracket-match">
                  ${renderMatchTeam(match.homeCode, match.homeName, match.homeGoals)}
                  ${renderMatchTeam(match.awayCode, match.awayName, match.awayGoals)}
                  <div class="match-meta">Winner: <span class="winner-line">${winnerName}</span></div>
                </div>
              `;
            })
            .join("")}
        </section>
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
          <td>${renderTeamIdentity(row)}</td>
          <td>${row.group}</td>
          <td>${row.fifaRank}</td>
          <td>${row.power.toFixed(1)}</td>
          <td class="cell-probability">${formatPercent(row.advanceProbability)}</td>
          <td class="cell-probability">${formatPercent(row.quarterfinalProbability)}</td>
          <td class="cell-probability">${formatPercent(row.semifinalProbability)}</td>
          <td class="cell-probability">${formatPercent(row.championProbability)}</td>
          <td>${row.avgGroupPoints.toFixed(2)}</td>
        </tr>
      `
    )
    .join("");
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
  buildStatus.textContent = "Ready.";
  setText(
    "summary-context",
    `${data.metadata.iterations} runs | ${data.metadata.scenario} scenario | host advantage ${data.metadata.hostAdvantage ? "on" : "off"} | FIFA snapshot ${state.metadata.rankingDate}`
  );

  renderSummary(data.summary);
  renderFeaturedTeam(data.featuredTeam);
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
