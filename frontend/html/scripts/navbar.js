import { getToken, logoutUser, getUserByEmail } from "./api.js";

export async function updateNavbarState() {
  const loggedOut = document.querySelector(".logged-out");
  const loggedIn = document.querySelector(".logged-in");
  const userNameEl = document.querySelector(".user-name");
  const userFunds = document.querySelector(".user-funds");
  const logoutBtn = document.querySelector(".logout-button");

  const token = getToken();

  if (token) {
    if (loggedOut) loggedOut.style.display = "none";
    if (loggedIn) loggedIn.style.display = "flex";

    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      const email = payload.sub;

      const user = await getUserByEmail(email);
      userNameEl.textContent = user?.name || "User";

      userFunds.textContent =
        user?.funds !== undefined ? `${user.funds} €` : "";

      if (user?.role === "admin") {
        const adminSpan = document.createElement("span");
        adminSpan.textContent = " (Admin)";
        adminSpan.style.color = "#ff3da5";
        adminSpan.style.cursor = "pointer";
        userNameEl.appendChild(adminSpan);

        adminSpan.onclick = () => {
          window.location.replace("../skin_management/index.html");
        };
      }
    } catch (error) {
      console.error("Erro ao carregar dados do utilizador:", error);
      userNameEl.textContent = "User";
    }

    if (logoutBtn) {
      logoutBtn.addEventListener("click", () => {
        logoutUser();
        window.location.replace("../login/index.html#login");
      });
    }


    const addIcon = document.querySelector(".add-icon");
    if (addIcon) {

      addIcon.style.cursor = "pointer";

      addIcon.addEventListener("click", () => {

        window.location.href = "../deposit_funds/index.html";
      });
    }

  } else {
    if (loggedOut) loggedOut.style.display = "flex";
    if (loggedIn) loggedIn.style.display = "none";
  }
}
