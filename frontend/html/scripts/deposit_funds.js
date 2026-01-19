import { addFunds } from "./api.js";

const form = document.querySelector("form");
const valueInput = form.querySelector('input[name="value"]');
const cardNumberInput = form.querySelector('#card_number');
const expDateInput = form.querySelector('#exp_date');
const cvvInput = form.querySelector('#cvv');

// Error spans
const valueError = document.createElement("span");
valueError.style.color = "red";
valueError.style.fontSize = "0.9rem";
valueInput.parentNode.appendChild(valueError);

const cardNumberError = document.createElement("span");
cardNumberError.style.color = "red";
cardNumberError.style.fontSize = "0.9rem";
cardNumberInput.parentNode.appendChild(cardNumberError);

const cvvError = document.createElement("span");
cvvError.style.color = "red";
cvvError.style.fontSize = "0.9rem";
cvvInput.parentNode.appendChild(cvvError);

const expDateError = document.createElement("span");
expDateError.style.color = "red";
expDateError.style.fontSize = "0.9rem";
expDateInput.parentNode.appendChild(expDateError);

// Max value
valueInput.setAttribute("max", "10000");

valueInput.addEventListener("input", () => {
    const amount = parseFloat(valueInput.value);
    if (isNaN(amount) || amount <= 0 || amount >= 10000) {
        valueError.textContent = "Please enter a valid deposit amount between 1 and 10,000.";
    } else {
        valueError.textContent = "";
    }
});

cardNumberInput.addEventListener("input", () => {
    cardNumberInput.value = cardNumberInput.value.replace(/\D/g, "").slice(0, 16);
    cardNumberError.textContent = cardNumberInput.value.length !== 16 ? "Card number must be exactly 16 digits." : "";
});

cvvInput.addEventListener("input", () => {
    cvvInput.value = cvvInput.value.replace(/\D/g, "").slice(0, 3);
    cvvError.textContent = cvvInput.value.length !== 3 ? "CVV must be exactly 3 digits." : "";
});

expDateInput.addEventListener("input", () => {
    const today = new Date();
    const exp = new Date(expDateInput.value);
    exp.setDate(exp.getDate() + 1);
    const year = exp.getFullYear();

    if (exp <= today) {
        expDateError.textContent = "Expiry date cannot be in the past.";
    } else if (year > 2999) {
        expDateError.textContent = "Expiry year cannot be later than 2999.";
    } else {
        expDateError.textContent = "";
    }
});

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const amount = parseFloat(valueInput.value);
    const cardNumber = cardNumberInput.value.trim();
    const expDate = expDateInput.value;
    const cvv = cvvInput.value.trim();

    let hasError = false;

    if (isNaN(amount) || amount <= 0 || amount >= 10000) {
        valueError.textContent = "Please enter a valid deposit amount between 1 and 10.000.";
        hasError = true;
    } else {
        valueError.textContent = "";
    }

    if (cardNumber.length !== 16) {
        cardNumberError.textContent = "Card number must be exactly 16 digits.";
        hasError = true;
    } else {
        cardNumberError.textContent = "";
    }

    if (cvv.length !== 3) {
        cvvError.textContent = "CVV must be exactly 3 digits.";
        hasError = true;
    } else {
        cvvError.textContent = "";
    }

    const today = new Date();
    const exp = new Date(expDate);
    exp.setDate(exp.getDate() + 1);
    const year = exp.getFullYear();
    if (exp <= today) {
        expDateError.textContent = "Expiry date cannot be in the past.";
        hasError = true;
    } else if (year > 2999) {
        expDateError.textContent = "Expiry year cannot be later than 2999.";
        hasError = true;
    } else {
        expDateError.textContent = "";
    }

    if (hasError) return;

    try {
        // Ensure amount is number
        await addFunds({ amount: amount });

        valueError.style.color = "green";
        valueError.textContent = `Deposit of €${amount.toFixed(2)} completed successfully!`;

        form.reset();

        // Redirect only after success
        setTimeout(() => {
            window.location.href = "../inventory/index.html";
        }, 1000);

    } catch (error) {
        console.error("Deposit error:", error);
        valueError.style.color = "red";
        valueError.textContent = `Failed to deposit funds: ${error?.message || JSON.stringify(error)}`;
    }
});
