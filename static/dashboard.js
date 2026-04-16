function attendanceLabel(attendance) {
  if (attendance === "yes") {
    return "Confirmé";
  }
  if (attendance === "no") {
    return "Décliné";
  }
  return "En attente";
}

function formatDate(value) {
  if (!value) {
    return "N/A";
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("fr-FR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(parsed);
}

function renderRows(responses) {
  const tableBody = document.getElementById("responses-table");

  if (!responses.length) {
    tableBody.innerHTML = '<tr><td colspan="6">Aucune réponse pour le moment.</td></tr>';
    return;
  }

  tableBody.innerHTML = "";

  responses.forEach((response) => {
    const row = document.createElement("tr");
    const notes = [
      response.dietary_requirements,
      response.song_request ? `Musique: ${response.song_request}` : "",
      response.message,
    ]
      .filter(Boolean)
      .join(" | ");

    const nameCell = document.createElement("td");
    nameCell.textContent = response.full_name;

    const statusCell = document.createElement("td");
    const status = document.createElement("span");
    status.className = `status status-${response.attendance}`;
    status.textContent = attendanceLabel(response.attendance);
    statusCell.appendChild(status);

    const guestsCell = document.createElement("td");
    guestsCell.textContent = String(response.guest_count);

    const contactCell = document.createElement("td");
    const emailLine = document.createElement("div");
    emailLine.textContent = response.email;
    const phoneLine = document.createElement("div");
    phoneLine.textContent = response.phone || "";
    contactCell.append(emailLine, phoneLine);

    const notesCell = document.createElement("td");
    notesCell.textContent = notes || "Aucune précision";

    const updatedCell = document.createElement("td");
    updatedCell.textContent = formatDate(response.updated_at);

    row.append(nameCell, statusCell, guestsCell, contactCell, notesCell, updatedCell);
    tableBody.appendChild(row);
  });
}

async function loadDashboard() {
  const response = await fetch("/api/rsvps");
  const payload = await response.json();

  document.getElementById("total-responses").textContent = payload.summary.total_responses;
  document.getElementById("confirmed-households").textContent = payload.summary.confirmed_households;
  document.getElementById("confirmed-guests").textContent = payload.summary.confirmed_guests;
  document.getElementById("tentative-households").textContent = payload.summary.tentative_households;

  renderRows(payload.responses);
}

document.addEventListener("DOMContentLoaded", async () => {
  try {
    await loadDashboard();
  } catch (error) {
    console.error("Impossible de charger le tableau de bord.", error);
  }
});
