import { adminCreateSkin, adminEditSkin, getAllSkins, adminDeleteSkin, getToken, getUserByEmail } from "./api.js";
import "./dropdown_style.js";
import "./main.js";

// DOM elements
const container = document.getElementById("skin_display");
const empty = document.getElementById("empty");
const searchInput = document.getElementById("search");
const filterType = document.getElementById("filter-type");
const filterSkin = document.getElementById("filter-skin");
const sortSelect = document.getElementById("sort");
const resetBtn = document.getElementById("reset");
const btnAdd = document.getElementById("btn-add");

const drawer = document.getElementById("drawer");
const drawerTitle = document.getElementById("drawer-title");
const drawerClose = document.getElementById("drawer-close");
const form = document.getElementById("skin-form");
const btnCancel = document.getElementById("btn-cancel");
const btnDelete = document.getElementById("btn-delete");
const btnSave = document.getElementById("btn-save");

const fType = document.getElementById("f-type");
const fSkin = document.getElementById("f-skin");
const fQuantity = document.getElementById("f-quantity");
const fFloat = document.getElementById("f-float");
const fLink = document.getElementById("f-link");
const fQuantityWrapper = fQuantity.parentElement;

let skins = [];

function refreshCustomSelect(select) {
  const next = select.nextElementSibling;
  if (next && next.classList.contains("custom-select")) next.remove();
  delete select.dataset.enhanced;
  document.dispatchEvent(new CustomEvent("force-enhance-select", { detail: select }));
}

function capitalize(s) {
  if (!s) return "";
  return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();
}

function normalizeFloat(f) {
  const map = {
    "factory new": "Factory New",
    "minimal wear": "Minimal Wear",
    "field-tested": "Field-Tested",
    "filed tested": "Field-Tested",
    "well-worn": "Well-Worn",
    "battle-scarred": "Battle-Scarred"
  };
  return map[f.toLowerCase()] || f;
}

// Drawer controls
function showDrawer() {
  drawer.classList.add("active");
  drawer.setAttribute("aria-hidden", "false");
}

function hideDrawer() {
  drawer.classList.remove("active");
  drawer.setAttribute("aria-hidden", "true");
  form.dataset.editing = "";
  btnDelete.style.display = "none";
}

// Populate filters
function populateFilters() {
  const types = [...new Set(skins.map(s => capitalize(s.type)))].sort();
  const names = [...new Set(skins.map(s => capitalize(s.name)))].sort();

  filterType.innerHTML = '<option value="all">All knife types</option>';
  filterSkin.innerHTML = '<option value="all">All finishes</option>';

  types.forEach(type => {
    const opt = document.createElement("option");
    opt.value = type;
    opt.textContent = type;
    filterType.appendChild(opt);
  });

  names.forEach(name => {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    filterSkin.appendChild(opt);
  });

  refreshCustomSelect(filterType);
  refreshCustomSelect(filterSkin);
}

function groupSkins(list) {
  const groups = {};
  list.forEach(s => {
    const key = `${s.type}|${s.name}|${s.float_value}`;
    if (!groups[key]) {
      groups[key] = { ...s, quantity: 1, idList: [s.id] };
    } else {
      groups[key].quantity++;
      groups[key].idList.push(s.id);
    }
  });
  return Object.values(groups);
}

// Render skins
function renderList(list) {
  container.innerHTML = "";
  if (!list.length) {
    empty.style.display = "block";
    empty.textContent = skins.length === 0
      ? "There are no skins in the system."
      : "No skins match your filters.";
    return;
  }
  empty.style.display = "none";

  list.forEach((s, idx) => {
    const card = document.createElement("div");
    card.className = "skin-card";
    card.dataset.id = s.id;

    card.innerHTML = `
      <div><div class="skin-name">${s.type} ${s.name}</div></div>
      <div class="skin-thumb"><img src="${s.link}" alt="${s.name}"></div>
      <div><div class="skin-sub">${s.float_value} — <strong>x${s.quantity}</strong></div></div>
      <div class="actions">
        <button class="btn btn-edit" data-action="edit" data-ids='${JSON.stringify(s.idList)}'>Edit</button>
        <button class="btn btn-danger" data-action="delete" data-ids='${JSON.stringify(s.idList)}'>Delete</button>
      </div>
    `;

    container.appendChild(card);
    setTimeout(() => card.classList.add("visible"), 70 * idx);
  });
}

// Filters & sorting
function applyFilters() {
  let out = skins.slice();
  const q = (searchInput.value || "").toLowerCase();

  if (q) out = out.filter(s => (s.name + s.type).toLowerCase().includes(q));
  if (filterType.value !== "all") out = out.filter(s => s.type.toLowerCase() === filterType.value.toLowerCase());
  if (filterSkin.value !== "all") out = out.filter(s => s.name.toLowerCase() === filterSkin.value.toLowerCase());

  const floatOrder = { "Factory New": 1, "Minimal Wear": 2, "Field-Tested": 3, "Well-Worn": 4, "Battle-Scarred": 5 };

  switch (sortSelect.value) {
    case "name-asc": out.sort((a, b) => a.name.localeCompare(b.name)); break;
    case "name-desc": out.sort((a, b) => b.name.localeCompare(a.name)); break;
    case "float-asc": out.sort((a, b) => (floatOrder[normalizeFloat(a.float_value)] || 99) - (floatOrder[normalizeFloat(b.float_value)] || 99)); break;
    case "float-desc": out.sort((a, b) => (floatOrder[normalizeFloat(b.float_value)] || 99) - (floatOrder[normalizeFloat(a.float_value)] || 99)); break;
  }

  renderList(groupSkins(out));
}

// =============================
// INITIAL LOAD WITH LOGIN CHECK
// =============================
document.addEventListener("DOMContentLoaded", async () => {
  try {
    const token = getToken();
    if (!token) {
      empty.style.display = "block";
      empty.textContent = "You must be logged in to access this page.";
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

    skins = await getAllSkins();

    if (skins.length === 0) {
      empty.style.display = "block";
      empty.textContent = "There are no skins in the system.";
      return;
    }

    populateFilters();
    applyFilters();
  } catch (err) {
    console.error(err);
    empty.style.display = "block";
    empty.textContent = "Failed to load skins.";
  }
})

// Add drawer
function openAdd() {
  drawerTitle.textContent = "Add Skin";
  form.dataset.editing = "";
  btnDelete.style.display = "none";

  fType.value = "";
  fSkin.value = "";
  fQuantity.value = 1;
  fFloat.value = "";
  fLink.value = "";

  fQuantityWrapper.style.display = "flex";
  fQuantity.setAttribute("required", "");
  showDrawer();
}

// Edit drawer
function openEdit(idList) {
  const ids = JSON.parse(idList);
  const first = skins.find(s => s.id === ids[0]);
  if (!first) {
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'Skins not found.',
      confirmButtonColor: '#3085d6'
    });
    return;
  }

  drawerTitle.textContent = `Edit ${ids.length} skins`;
  form.dataset.editing = JSON.stringify(ids);
  btnDelete.style.display = "";

  fType.value = first.type;
  fSkin.value = first.name;
  fFloat.value = normalizeFloat(first.float_value);
  fLink.value = first.link;

  fQuantityWrapper.style.display = "none";
  fQuantity.removeAttribute("required");
  showDrawer();
}

// Delete skins
async function doDelete(idList) {
  const ids = JSON.parse(idList);
  const { isConfirmed } = await Swal.fire({
    title: `Delete ${ids.length} skin(s)?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Yes, delete',
    cancelButtonText: 'Cancel',
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33'
  });

  if (!isConfirmed) return;

  try {
    for (const id of ids) await adminDeleteSkin(id);
    skins = await getAllSkins();
    populateFilters();
    applyFilters();
    Swal.fire({
      icon: 'success',
      title: 'Deleted!',
      text: `${ids.length} skin(s) deleted.`,
      confirmButtonColor: '#3085d6'
    });
    hideDrawer();
  } catch (err) {
    console.error("Error deleting skins:", err);
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'Failed to delete skins: ' + err.message,
      confirmButtonColor: '#3085d6'
    });
  }
}

// Form submit
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const type = capitalize(fType.value.trim());
  const name = capitalize(fSkin.value.trim());
  const quantity = Number(fQuantity.value) || 1;
  const float_value = fFloat.value.trim() || "Factory New";
  const link = fLink.value.trim();

  const payload = { name, type, float_value, link, owner_id: 0, date_created: new Date().toISOString() };
  const editing = form.dataset.editing;
  const ids = editing ? JSON.parse(editing) : null;

  try {
    if (ids && ids.length) {
      for (const id of ids) await adminEditSkin(id, payload);
    } else {
      for (let i = 0; i < quantity; i++) {
        payload.id = 0;
        await adminCreateSkin(payload);
      }
    }
    skins = await getAllSkins();
    populateFilters();
    applyFilters();
    hideDrawer();
    Swal.fire({
      icon: 'success',
      title: 'Success!',
      text: 'Skin saved successfully!',
      confirmButtonColor: '#3085d6'
    });
  } catch (err) {
    console.error("Error saving skin:", err);
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'Failed to save skin: ' + err.message,
      confirmButtonColor: '#3085d6'
    });
  }
});

// Delete button
btnDelete.addEventListener("click", async () => {
  const ids = JSON.parse(form.dataset.editing);
  if (!ids || !ids.length) return;

  const { isConfirmed } = await Swal.fire({
    title: `Delete ${ids.length} skin(s)?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Yes, delete',
    cancelButtonText: 'Cancel',
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33'
  });

  if (!isConfirmed) return;

  try {
    for (const id of ids) await adminDeleteSkin(id);
    skins = await getAllSkins();
    populateFilters();
    applyFilters();
    hideDrawer();
    Swal.fire({
      icon: 'success',
      title: 'Deleted!',
      text: `${ids.length} skin(s) deleted.`,
      confirmButtonColor: '#3085d6'
    });
  } catch (err) {
    console.error("Error deleting skins:", err);
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'Failed to delete skins: ' + err.message,
      confirmButtonColor: '#3085d6'
    });
  }
});


// Drawer buttons
btnAdd.addEventListener("click", openAdd);
drawerClose.addEventListener("click", hideDrawer);
btnCancel.addEventListener("click", hideDrawer);

// Edit/Delete on cards
container.addEventListener("click", (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;

  const action = btn.dataset.action;
  const ids = btn.dataset.ids;
  if (!action) return;

  if (action === "edit") openEdit(ids);
  else if (action === "delete") doDelete(ids);
});

// Filters
[searchInput, filterType, filterSkin, sortSelect].forEach(el => el.addEventListener("input", applyFilters));

resetBtn.addEventListener("click", () => {
  searchInput.value = "";
  filterType.value = "all";
  filterSkin.value = "all";
  sortSelect.value = "default";
  applyFilters();
});
