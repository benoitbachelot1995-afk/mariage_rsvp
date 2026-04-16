async function loadThankYouConfig() {
  const response = await fetch("/api/event");
  const config = await response.json();

  document.getElementById("thank-you-couple").textContent = config.couple_names;
  document.getElementById("thank-you-date").textContent = config.wedding_date;
  document.getElementById("thank-you-venue").textContent = config.venue;
  document.title = `Merci | ${config.couple_names}`;
}

function buildMessage(name, attendance) {
  const firstName = (name || "").trim().split(/\s+/)[0] || "Merci";

  if (attendance === "no") {
    return {
      title: `Merci ${firstName}`,
      message:
        "Votre réponse a bien été enregistrée. Même si vous ne pouvez pas être présent(e), nous sommes très touchés d’avoir de vos nouvelles.",
    };
  }

  if (attendance === "maybe") {
    return {
      title: `Merci ${firstName}`,
      message:
        "Votre réponse a bien été enregistrée. Nous gardons votre confirmation en attente et serons ravis de vous compter parmi nous si vous pouvez vous joindre à la fête.",
    };
  }

  return {
    title: `Merci ${firstName}`,
    message:
      "Votre confirmation a bien été prise en compte et nous sommes très heureux de vous compter parmi nous pour cette journée.",
  };
}

document.addEventListener("DOMContentLoaded", async () => {
  const params = new URLSearchParams(window.location.search);
  const name = params.get("name");
  const attendance = params.get("attendance");
  const content = buildMessage(name, attendance);

  document.getElementById("thank-you-title").textContent = content.title;
  document.getElementById("thank-you-message").textContent = content.message;

  try {
    await loadThankYouConfig();
  } catch (error) {
    console.error("Impossible de charger la configuration de la page merci.", error);
  }
});
