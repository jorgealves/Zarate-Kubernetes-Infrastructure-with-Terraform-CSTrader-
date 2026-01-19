import { loginUser, registerUser } from "./api.js";

document.addEventListener("DOMContentLoaded", () => {
  // Toggle password visibility for any field
  const togglePassword = (toggleBtn, input) => {
    if (!toggleBtn || !input) return;
    toggleBtn.addEventListener("click", () => {
      const isPassword = input.type === "password";
      input.type = isPassword ? "text" : "password";
      toggleBtn.classList.toggle("fa-eye");
      toggleBtn.classList.toggle("fa-eye-slash");
    });
  };

  togglePassword(
    document.querySelector("#togglePasswordLogin"),
    document.querySelector("#password-login")
  );

  togglePassword(
    document.querySelector("#togglePasswordRegister"),
    document.querySelector("#password-register")
  );

  togglePassword(
    document.querySelector("#toggleCPasswordRegister"),
    document.querySelector("#cpassword-register")
  );

  const flipContainer = document.getElementById("authFlip");

  window.addEventListener("DOMContentLoaded", () => {
    if (window.location.hash === "#register") {
      flipContainer.classList.add("flipped");
    } else {
      flipContainer.classList.remove("flipped");
    }
  });

  document.getElementById("goToRegister")?.addEventListener("click", e => {
    e.preventDefault();
    flipContainer?.classList.add("flipped");
  });

  document.getElementById("goToLogin")?.addEventListener("click", e => {
    e.preventDefault();
    flipContainer?.classList.remove("flipped");
  });
});


// LOGIN FORM
document.querySelector(".front form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const email = document.getElementById("email-login").value.trim();
  const password = document.getElementById("password-login").value.trim();

  if (!email || !password) {
    return Swal.fire("Missing fields", "Please fill in all required fields.", "warning");
  }

  try {
    await loginUser(email, password);
    Swal.fire({
      title: "Login successful!",
      icon: "success",
      timer: 1500,
      showConfirmButton: false
    }).then(() => window.location.href = "/index.html");
  } catch (err) {
    Swal.fire("Error", "Invalid email or password" , "error");
  }
});

// REGISTER FORM
document.querySelector(".back form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const username = document.getElementById("username-register").value.trim();
  const email = document.getElementById("email-register").value.trim();
  const password = document.getElementById("password-register").value.trim();
  const cpassword = document.getElementById("cpassword-register").value.trim();

  // Lista de validações com mensagens de erro
  const validations = [
    { condition: !username || !email || !password || !cpassword, msg: "Please fill in all fields." },
    { condition: username.length < 3 || username.length > 20, msg: "Username must be between 3 and 20 characters." },
    { condition: !/^[a-zA-Z0-9_-]+$/.test(username), msg: "Username can only contain letters, numbers, hyphens, or underscores." },
    { condition: !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email), msg: "Please enter a valid email address." },
    { condition: password.length < 8, msg: "Password must be at least 8 characters long." },
    {
      condition: !/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}/.test(password),
      msg: "Password must include uppercase, lowercase, number, and symbol."
    },
    { condition: password.includes(username), msg: "Password cannot contain your username." },
    { condition: cpassword !== password, msg: "Passwords do not match." }
  ];

  const invalid = validations.find(v => v.condition);
  if (invalid) {
    return Swal.fire("Warning", invalid.msg, "warning");
  }

  try {
    await registerUser(username, email, password, cpassword);
    Swal.fire({
      title: "Account created successfully!",
      text: "You can log in now.",
      icon: "success",
      confirmButtonText: "OK"
    }).then(() => {
      document.getElementById("authFlip")?.classList.remove("flipped");
    });
  } catch (err) {
    Swal.fire("Error", err.message || "Unable to create account. Please try again.", "error");
  }
});
