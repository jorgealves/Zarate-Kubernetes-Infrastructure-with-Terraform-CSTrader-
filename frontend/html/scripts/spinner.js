export function showSpinner() {
  document.getElementById("loading-spinner").classList.remove("hidden");
}

export function hideSpinner() {
  document.getElementById("loading-spinner").classList.add("hidden");
}