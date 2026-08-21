const form = document.getElementById("checkin-form");
const attendeeInput = document.getElementById("attendee-id");
const button = document.getElementById("checkin-button");

const result = document.getElementById("result");
const message = document.getElementById("message");
const status = document.getElementById("status");
const jobId = document.getElementById("job-id");

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const attendee_id = attendeeInput.value.trim();

    if (!attendee_id) {
        return;
    }

    button.disabled = true;
    button.textContent = "PROCESSING...";

    result.classList.remove("hidden");

    message.textContent = "Sending check-in...";
    status.textContent = "";
    jobId.textContent = "";

    try {
        const response = await fetch("/check-in", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                attendee_id: attendee_id
            })
        });

        const data = await response.json();

        message.textContent = data.message;

        if (response.status === 202) {
            status.textContent = `Status: ${data.status}`;
            jobId.textContent = `Job ID: ${data.job_id}`;
        } else {
            status.textContent = `Status: ${response.status}`;

            if (data.attendee) {
                jobId.textContent = `Existing Job ID: ${data.attendee.job_id}`;
            }
        }

    } catch (error) {
        message.textContent = "Unable to connect to Meridian.";
        status.textContent = "Please make sure the Flask server is running.";
        console.error(error);
    } finally {
        button.disabled = false;
        button.textContent = "CHECK IN";
    }
});
