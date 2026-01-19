import { getMySkins, getToken, getUserByEmail, marketplaceAddSkin, transactionHistory } from "./api.js";
import "./dropdown_style.js";
import "./main.js";

const container = document.getElementById("skin_display");
const empty = document.getElementById("empty");
const searchInput = document.getElementById("search");
const filterType = document.getElementById("filter-type");
const filterSkin = document.getElementById("filter-skin");
const sortSelect = document.getElementById("sort");
const resetBtn = document.getElementById("reset");

let skins = [];
let viewingHistory = false;

const floatOrder = {
  "Factory New": 1,
  "Minimal Wear": 2,
  "Field-Tested": 3,
  "Well-Worn": 4,
  "Battle-Scarred": 5,
};

function normalizeFloat(f) {
  const map = {
    "factory new": "Factory New",
    "minimal wear": "Minimal Wear",
    "field-tested": "Field-Tested",
    "well-worn": "Well-Worn",
    "battle-scarred": "Battle-Scarred",
  };
  return map[f.toLowerCase()] || f;
}


// RENDER INVENTORY LIST

function renderList(list) {
  container.classList.add("inventory-grid");
  container.classList.remove("history-view");

  container.innerHTML = "";
  if (!list.length) {
    empty.style.display = "block";
    empty.textContent = skins.length === 0
      ? "You have no skins in your inventory."
      : "No skins match your filters.";
    return;
  }

  empty.style.display = "none";

  list.forEach((s, idx) => {
    const card = document.createElement("div");
    card.className = "skin-card flip-card";

    const inner = document.createElement("div");
    inner.className = "flip-inner";

    // FRONT
    const front = document.createElement("div");
    front.className = "flip-front";
    front.innerHTML = `
      <div class="skin-thumb"><img src="${s.link}" alt="${s.name}"></div>
      <div class="skin-info">
        <div class="skin-name">${s.name}</div>
        <div class="skin-sub">${s.float}</div>
      </div>
      <button class="btn btn-buynow">Sell Now</button>
    `;

    // BACK
    const back = document.createElement("div");
    back.className = "flip-back";
    back.innerHTML = `
      <div class="skin-name">${s.name}</div>
      <div class="skin-sub">Type: ${s.knifeType} | Finish: ${s.skinType} | Float: ${s.float}</div>
      <form class="sell-form">
        <input type="number" min="0" placeholder="Enter price" class="sell-value" required />
        <button type="submit" class="btn btn-sell">Sell</button>
        <button type="button" class="btn btn-cancel-back">Cancel</button>
      </form>
    `;

    inner.appendChild(front);
    inner.appendChild(back);
    card.appendChild(inner);
    container.appendChild(card);

    setTimeout(() => card.classList.add("visible"), 70 * idx);

    // Flip events
    front.querySelector(".btn-buynow").addEventListener("click", () => card.classList.add("flipped"));
    back.querySelector(".btn-cancel-back").addEventListener("click", () => card.classList.remove("flipped"));


    const form = back.querySelector(".sell-form");
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const price = parseFloat(back.querySelector(".sell-value").value);
      if (isNaN(price) || price <= 0) {
        Swal.fire({
          icon: 'warning',
          title: 'Invalid price',
          text: 'Please enter a valid price.',
          confirmButtonColor: '#3085d6'
        });
        return;
      }

      const { isConfirmed } = await Swal.fire({
        title: `Confirm sale of ${s.name}?`,
        text: `Price: €${price}`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Yes, sell it!',
        cancelButtonText: 'Cancel',
        confirmButtonColor: '#115f0cff',
        cancelButtonColor: 'rgba(121, 14, 81, 1)'
      });

      if (!isConfirmed) return;

      try {
        await marketplaceAddSkin({ id: s.id, value: price });
        await Swal.fire({
          icon: 'success',
          title: 'Success!',
          text: 'Skin listed successfully!',
          confirmButtonColor: '#3085d6'
        });
        location.reload();
      } catch (err) {
        console.error(err);
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'Failed to list skin.',
          confirmButtonColor: '#3085d6'
        });
      }
    });

  });
}

// =============================
// DROPDOWNS & FILTERS
// =============================
function refreshCustomSelect(select) {
  const next = select.nextElementSibling;
  if (next && next.classList.contains("custom-select")) next.remove();
  delete select.dataset.enhanced;
  document.dispatchEvent(new CustomEvent("force-enhance-select", { detail: select }));
}

function populateDropdowns(skins) {
  const knifeTypes = [...new Set(skins.map(s => s.knifeType).filter(Boolean))].sort();
  const skinTypes = [...new Set(skins.map(s => s.skinType).filter(Boolean))].sort();

  filterType.innerHTML = `<option value="all">All knife types</option>`;
  knifeTypes.forEach(type => filterType.append(new Option(type, type)));

  filterSkin.innerHTML = `<option value="all">All finishes</option>`;
  skinTypes.forEach(type => filterSkin.append(new Option(type, type)));

  refreshCustomSelect(filterType);
  refreshCustomSelect(filterSkin);
}

function applyFilters() {
  let out = skins.slice();
  const q = searchInput.value.toLowerCase();

  // SEARCH
  if (q)
    out = out.filter((s) =>
      (s.name + s.knifeType + s.skinType).toLowerCase().includes(q)
    );

  // FILTER KNIFE TYPE
  if (filterType.value !== "all")
    out = out.filter((s) => s.knifeType === filterType.value);

  // FILTER SKIN TYPE
  if (filterSkin.value !== "all")
    out = out.filter((s) => s.skinType === filterSkin.value);

  // SORT
  switch (sortSelect.value) {
    case "name-asc":
      out.sort((a, b) => a.name.localeCompare(b.name));
      break;

    case "name-desc":
      out.sort((a, b) => b.name.localeCompare(a.name));
      break;

    case "float-asc":
      out.forEach((s) => (s.float = normalizeFloat(s.float)));
      out.sort(
        (a, b) => (floatOrder[a.float] || 99) - (floatOrder[b.float] || 99)
      );
      break;

    case "float-desc":
      out.forEach((s) => (s.float = normalizeFloat(s.float)));
      out.sort(
        (a, b) => (floatOrder[b.float] || 99) - (floatOrder[a.float] || 99)
      );
      break;
  }

  // RENDER
  renderList(out);
}


// =============================
// INITIAL LOAD
// =============================
document.addEventListener("DOMContentLoaded", async () => {
  try {
    const token = getToken();
    if (!token) {
      empty.style.display = "block";
      window.location.replace("../login/index.html#login");
      return;
    }

    let payload;
    try {
      payload = JSON.parse(atob(token.split(".")[1]));
    } catch {
      empty.style.display = "block";
      empty.textContent = "Your session has expired. Please log in again.";
      return;
    }

    await getUserByEmail(payload.sub);

    skins = await getMySkins();

    if (skins.length === 0) {
      empty.style.display = "block";
      empty.textContent = "You have no skins in your inventory.";
      return;
    }

    populateDropdowns(skins);
    applyFilters();
  } catch (err) {
    console.error(err);
    empty.style.display = "block";
    empty.textContent = "Failed to load your inventory.";
  }
});


// =============================
//   TRANSACTION HISTORY
// =============================
const transactionBtn = document.getElementById("transaction_history");

transactionBtn.addEventListener("click", async () => {
  viewingHistory = !viewingHistory;

  if (viewingHistory) {
    const history = await transactionHistory();
    renderTransactionTable(history);
    transactionBtn.innerText = "View Inventory";
  } else {
    container.classList.add("inventory-grid");
    renderList(skins);
    transactionBtn.innerText = "Transaction History";
  }
});

// =============================
// RENDER TRANSACTION TABLE
// =============================
function renderTransactionTable(data) {
  container.classList.remove("inventory-grid");
  container.classList.add("history-view");

  container.innerHTML = "";
  empty.style.display = "none";

  // 👉 Ordenar do ID MAIOR para o MENOR
  data.sort((a, b) => b.id - a.id);

  const table = document.createElement("table");
  table.className = "transaction-table";

  // 👉 Removido o campo ID do header e do body
  table.innerHTML = `
    <thead>
      <tr>
        <th>Amount (€)</th>
        <th>Type</th>
        <th>Date</th>
      </tr>
    </thead>
    <tbody>
      ${data
      .map(
        t => `
        <tr>
          <td>€${parseFloat(t.amount).toFixed(2)}</td>
          <td>${t.type}</td>
          <td>${new Date(t.date).toLocaleString()}</td>
        </tr>`
      )
      .join("")}
    </tbody>
  `;

  container.appendChild(table);
}



[searchInput, filterType, filterSkin, sortSelect].forEach((el) =>
  el.addEventListener("input", applyFilters)
);


// =============================
// RESET BUTTON
// =============================
resetBtn.addEventListener("click", () => {
  searchInput.value = "";
  filterType.value = "all";
  filterSkin.value = "all";
  sortSelect.value = "default";
  applyFilters();
});