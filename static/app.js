async function loadEventConfig() {
  const response = await fetch("/api/event");
  const config = await response.json();

  document.getElementById("couple-names").textContent = config.couple_names;
  document.getElementById("hero-message").textContent = config.hero_message;
  document.getElementById("wedding-date").textContent = config.wedding_date;
  document.getElementById("ceremony-time").textContent = config.ceremony_time;
  document.getElementById("venue").textContent = config.venue;
  document.getElementById("response-deadline").textContent = config.response_deadline;
  document.title = `RSVP | ${config.couple_names}`;
}

function updateGuestCountState(form) {
  const attendance = form.querySelector('input[name="attendance"]:checked')?.value;
  const guestCountInput = form.querySelector('input[name="guest_count"]');

  if (!guestCountInput) {
    return;
  }

  if (attendance === "no") {
    guestCountInput.value = 0;
    guestCountInput.setAttribute("disabled", "disabled");
  } else {
    if (Number(guestCountInput.value) < 1) {
      guestCountInput.value = 1;
    }
    guestCountInput.removeAttribute("disabled");
  }
}

async function handleSubmit(event) {
  event.preventDefault();

  const form = event.currentTarget;
  const feedback = document.getElementById("form-feedback");
  const submitButton = form.querySelector('button[type="submit"]');

  updateGuestCountState(form);

  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());
  payload.guest_count = Number(payload.guest_count || 0);

  submitButton.disabled = true;
  feedback.textContent = "Enregistrement en cours...";
  feedback.dataset.state = "loading";

  try {
    const response = await fetch("/api/rsvp", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "Une erreur inattendue est survenue.");
    }

    feedback.textContent = result.message;
    feedback.dataset.state = "success";
    form.reset();
    form.querySelector('input[value="yes"]').checked = true;
    form.querySelector('input[name="guest_count"]').value = 1;
    updateGuestCountState(form);
  } catch (error) {
    feedback.textContent = error.message;
    feedback.dataset.state = "error";
  } finally {
    submitButton.disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  const form = document.getElementById("rsvp-form");

  try {
    await loadEventConfig();
  } catch (error) {
    console.error("Impossible de charger la configuration de l'événement.", error);
  }

  if (!form) {
    return;
  }

  form.addEventListener("submit", handleSubmit);
  form.addEventListener("change", () => updateGuestCountState(form));
  updateGuestCountState(form);
});
