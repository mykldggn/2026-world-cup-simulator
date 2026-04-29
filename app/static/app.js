const state = {
  metadata: null,
  teamIndex: {},
  scenario: "balanced",
};

const CONFED_COLORS = {
  UEFA: ["#2d6cdf", "#84a8ff"],
  CONMEBOL: ["#c89b2d", "#f0d485"],
  Concacaf: ["#2ca58d", "#7addc8"],
  AFC: ["#bf4a3d", "#f19589"],
  CAF: ["#2f9e44", "#91d59d"],
  OFC: ["#7d53e4", "#b59fff"],
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

function teamBadgeStyle(team) {
  const colors = CONFED_COLORS[team.confederation] || ["#5c6b7b", "#9aa7b4"];
  return `--badge-start:${colors[0]};--badge-end:${colors[1]};`;
}

function renderTeamIdentity(team, metaText = "") {
  return `
    <div class="team-identity">
      <span class="team-badge" style="${teamBadgeStyle(team)}">${team.code}</span>
      <span class="team-flag" aria-hidden="true">${flagFromCode(team.flagCode)}</span>
      <div class="team-text">
        <strong>${team.name}</strong>
        ${metaText ? `<span class="team-meta">${metaText}</span>` : ""}
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
    ${renderTeamIdentity(featuredTeam, `${featuredTeam.confederation || ""}`)}
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
