export async function loadNavbar() {
  const navbarContainer = document.getElementById("navbar");
  if (!navbarContainer) return;

  const response = await fetch("../components/navbar.html");
  const html = await response.text();
  navbarContainer.innerHTML = html;
}

export async function loadFilters() {
  const filterContainer = document.getElementById("load_filter");
  if (!filterContainer) return;

  const response = await fetch("../components/filter.html");
  const html = await response.text();
  filterContainer.innerHTML = html;
}

export async function loadModalMaket() {
  const container = document.getElementById("modal-market");
  if (!container) return;

  const response = await fetch("../components/modal_marketplace.html");
  const html = await response.text();

  container.innerHTML = html;

  return container; 
}
