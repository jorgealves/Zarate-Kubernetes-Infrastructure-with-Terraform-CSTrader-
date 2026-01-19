/* const API_BASE_URL = "http://localhost:8000"; */
const API_BASE_URL = "/api";
import { showSpinner, hideSpinner } from "./spinner.js";

// -----------------------------
// TOKEN
// -----------------------------
export function getToken() {
  return localStorage.getItem("token");
}

function authHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${getToken()}`,
  };
}

// -----------------------------
// LOGIN
// -----------------------------
export async function loginUser(email, password) {
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Erro ao fazer login.");

  localStorage.setItem("token", data.access_token);
  return data;
}

// -----------------------------
// REGISTAR UTILIZADOR
// -----------------------------
export async function registerUser(name, email, password) {
  const response = await fetch(`${API_BASE_URL}/register_user`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name,
      email,
      password,
      funds: 0,
      role: "player",
    }),
  });

  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Erro ao criar conta.");
  return data;
}

// -----------------------------
// GET USERS
// -----------------------------
export async function getUsers() {
  const response = await fetch(`${API_BASE_URL}/get_users`);
  const data = await response.json();

  if (!response.ok)
    throw new Error(data.detail || "Erro ao obter utilizadores.");
  return data;
}

// -----------------------------
// GET USER BY EMAIL
// -----------------------------
export async function getUserByEmail(email) {
  const token = getToken();
  const encoded = encodeURIComponent(email);

  const response = await fetch(`${API_BASE_URL}/get_user/${encoded}`, {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });
  const data = await response.json();

  if (!response.ok)
    throw new Error(data.detail || "Erro ao buscar utilizador.");
  return data.user;
}

// -----------------------------
// /users/me  → GET MY DATA
// -----------------------------
export async function getLoggedUser() {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_BASE_URL}/users/me`, {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    throw new Error(`Erro ao buscar user: ${res.status}`);
  }

  return res.json();
}

// -----------------------------
// LOGOUT
// -----------------------------
export function logoutUser() {
  localStorage.removeItem("token");
}

// -----------------------------
// /inventory → GET MY SKINS
// -----------------------------
export async function getMySkins() {
  const response = await fetch(`${API_BASE_URL}/inventory`, {
    headers: authHeaders(),
  });

  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Erro ao obter skins.");

  const mapped = (data.skins || []).map((s) => {
    const knife = s.type || "";
    const skin = s.name || "";

    const displayName =
      `${knife.charAt(0).toUpperCase() + knife.slice(1)} ` +
      `${skin.charAt(0).toUpperCase() + skin.slice(1)}`;

    return {
      id: s.id,
      name: displayName, // <--- só para mostrar no front-end
      knifeType: knife, // <--- campo original
      skinType: skin, // <--- campo original (vem de s.name)
      float: s.float_value || "Unknown",
      value: s.value ?? 0,
      link: s.link || "/path/to/placeholder.png",
    };
  });

  return mapped;
}

// -----------------------------
// /user/skins/{user_id} GET Skins por ID
// -----------------------------
export async function getUserSkinsById(userId) {
  const response = await fetch(`${API_BASE_URL}/user/skins/${userId}`, {
    headers: authHeaders(),
  });

  const data = await response.json();
  if (!response.ok)
    throw new Error(data.detail || "Erro ao obter skins do utilizador.");
  return data;
}

// -----------------------------
// POST /admin/skins → Criar skin (ADMIN)
// -----------------------------
export async function adminCreateSkin(skinData) {
  showSpinner();
  try {
    const payload = {
      id: 0,
      name: skinData.name,
      type: skinData.type,
      skin_type: skinData.skin_type,
      float_value: skinData.float_value,
      value: skinData.value,
      link: skinData.link,
      date_created: new Date().toISOString(),
    };

    const response = await fetch(`${API_BASE_URL}/admin/skins`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Erro ao criar skin.");

    return data;
  } finally {
    hideSpinner();
  }
}

// -----------------------------
// PUT /admin/skin/edit/{skin_id} → Editar skin
// -----------------------------
export async function adminEditSkin(skinId, skinData) {
  showSpinner();
  try {
    const response = await fetch(`${API_BASE_URL}/admin/skin/edit/${skinId}`, {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify(skinData),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Erro ao editar skin.");
    return data;
  } finally {
    hideSpinner();
  }
}

// -----------------------------
// GET SKINS FOR MARKETPLACE
// -----------------------------
export async function getMarketplace() {
  const response = await fetch(`${API_BASE_URL}/marketplace/skins`, {
    method: "GET",
    headers: authHeaders(),
  });

  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Erro ao obter skins.");

  const mapped = (data || []).map((s) => {
    const knife = s.type || "";
    const skin = s.name || "";

    const displayName =
      `${knife.charAt(0).toUpperCase() + knife.slice(1)} ` +
      `${skin.charAt(0).toUpperCase() + skin.slice(1)}`;

    return {
      id: s.id,
      name: displayName,
      knifeType: knife,
      skinType: skin,
      float: s.float_value || "Unknown",
      value: s.value ?? 0,
      link: s.link || "/path/to/placeholder.png",
    };
  });

  console.log(mapped);
  return mapped;
}

// -----------------------------
// COMPRAR SKIN
// -----------------------------
export async function buySkin(skinId) {
  try {
    const response = await fetch(`${API_BASE_URL}/buy_skin/${skinId}`, {
      /*mudar endpoint*/ method: "POST",
      headers: authHeaders(),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Erro ao comprar skin.");
    return data;
  } catch (err) {
    console.error("Erro ao comprar skin:", err);
    throw err;
  }
}

// -----------------------------
// GET Skins do Utilizador no Marketplace
// -----------------------------
export async function getUserMarketplace() {
  const token = getToken();
  if (!token) throw new Error("Token inválido.");

  const payload = JSON.parse(atob(token.split(".")[1]));
  const email = payload.sub;

  const user = await getUserByEmail(email);
  if (!user) throw new Error("Utilizador não encontrado.");

  const response = await fetch(`${API_BASE_URL}/marketplace/skins`, {
    method: "GET",
    headers: authHeaders(),
  });

  const allSkins = await response.json();
  if (!response.ok)
    throw new Error(allSkins.detail || "Erro ao obter marketplace.");

  const userSkins = allSkins.filter((skin) => skin.owner_id === user.id);

  return userSkins;
}

// -----------------------------
// Remover SKIN do marketplace
// -----------------------------
export async function removeSkin(skinId) {
  const response = await fetch(
    `${API_BASE_URL}/marketplace/remove/skin/${skinId}`,
    {
      method: "DELETE",
      headers: authHeaders(),
    }
  );

  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Erro ao eliminar skin.");

  return data;
}

// -----------------------------
// POST /trocas → Criar transação de compra
// -----------------------------
export async function createTrade(idUser, idSkin) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/marketplace/buy/skin/${idSkin}`,
      {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({
          id_user: idUser,
          id_skin: idSkin,
        }),
      }
    );

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Erro ao criar troca.");

    return data;
  } catch (err) {
    console.error("Erro ao enviar troca:", err);
    throw err;
  }
}

export async function getAllSkins() {
  const response = await fetch(`${API_BASE_URL}/skins/all`, {
    method: "GET",
    headers: authHeaders(),
  });

  const data = await response.json();
  if (!response.ok)
    throw new Error(data.detail || "Erro ao obter todas as skins.");

  return data;
}

export async function adminDeleteSkin(skinId) {
  showSpinner();
  try {
    const response = await fetch(
      `${API_BASE_URL}/admin/skin/delete/${skinId}`,
      {
        method: "DELETE",
        headers: authHeaders(),
      }
    );

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Erro ao eliminar skin.");

    return data;
  } finally {
    hideSpinner();
  }
}

// -----------------------------
// POST /marketplace/add → Listar skin no marketplace
// -----------------------------
export async function marketplaceAddSkin({ id, value }) {
  if (!id) throw new Error("Skin ID is required.");
  if (value == null || value < 0)
    throw new Error("Value must be a positive number.");

  const payload = {
    skin_id: id,
    value: value,
  };

  console.log("Listing skin with payload:", payload);

  const response = await fetch(`${API_BASE_URL}/marketplace/add/skin`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok)
    throw new Error(data.detail || "Erro ao adicionar skin ao marketplace.");

  return data;
}

export async function addFunds({ amount }) {
  if (amount == null || isNaN(amount) || amount <= 0) {
    throw new Error("Amount must be a positive number.");
  }

  console.log("Depositing funds:", amount);

  const response = await fetch(`${API_BASE_URL}/wallet/deposit`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ amount }),
  });

  const data = await response.json();
  if (!response.ok)
    throw new Error(data.detail || "Error while depositing funds.");

  return data;
}

export async function transactionHistory() {
  const response = await fetch(`${API_BASE_URL}/transactions/history`, {
    method: "GET",
    headers: authHeaders(),
  });
  const data = await response.json();
  if (!response.ok)
    throw new Error(data.detail || "Error while fetching transaction history.");

  return data;
}


export async function getMyMarketplace() {
  const response = await fetch(`${API_BASE_URL}/marketplace/user/skins`, {
    method: "GET",
    headers: authHeaders(),
  });

  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Erro ao obter skins.");

  const mapped = (data || []).map((s) => {
    const knife = s.type || "";
    const skin = s.name || "";

    const displayName =
      `${knife.charAt(0).toUpperCase() + knife.slice(1)} ` +
      `${skin.charAt(0).toUpperCase() + skin.slice(1)}`;

    return {
      id: s.id,
      name: displayName,
      knifeType: knife,
      skinType: skin,
      float: s.float_value || "Unknown",
      value: s.value ?? 0,
      link: s.link || "/path/to/placeholder.png",
    };
  });

  return mapped;
}