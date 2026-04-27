const API_BASE = `${window.location.origin}/api`;

async function apiFetch(path, options = {}) {
  const res = await fetch(API_BASE + path, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "API-Fehler");
  }
  if (res.status === 204) return null;
  return res.json();
}

const api = {
  // Products
  getProducts: () => apiFetch("/products/"),
  getProduct: (id) => apiFetch(`/products/${id}`),
  createProduct: (data) => apiFetch("/products/", { method: "POST", body: JSON.stringify(data) }),
  updateProduct: (id, data) => apiFetch(`/products/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteProduct: (id) => apiFetch(`/products/${id}`, { method: "DELETE" }),

  // Emission Factors
  getEFs: () => apiFetch("/emission-factors/"),
  getEF: (id) => apiFetch(`/emission-factors/${id}`),
  createEF: (data) => apiFetch("/emission-factors/", { method: "POST", body: JSON.stringify(data) }),
  updateEF: (id, data) => apiFetch(`/emission-factors/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteEF: (id) => apiFetch(`/emission-factors/${id}`, { method: "DELETE" }),

  // Inventory
  getMaterials: (pid) => apiFetch(`/inventory/materials/${pid}`),
  createMaterial: (data) => apiFetch("/inventory/materials/", { method: "POST", body: JSON.stringify(data) }),
  updateMaterial: (id, data) => apiFetch(`/inventory/materials/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteMaterial: (id) => apiFetch(`/inventory/materials/${id}`, { method: "DELETE" }),

  getEnergy: (pid) => apiFetch(`/inventory/energy/${pid}`),
  createEnergy: (data) => apiFetch("/inventory/energy/", { method: "POST", body: JSON.stringify(data) }),
  updateEnergy: (id, data) => apiFetch(`/inventory/energy/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteEnergy: (id) => apiFetch(`/inventory/energy/${id}`, { method: "DELETE" }),

  getTransport: (pid) => apiFetch(`/inventory/transport/${pid}`),
  createTransport: (data) => apiFetch("/inventory/transport/", { method: "POST", body: JSON.stringify(data) }),
  updateTransport: (id, data) => apiFetch(`/inventory/transport/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteTransport: (id) => apiFetch(`/inventory/transport/${id}`, { method: "DELETE" }),

  getWaste: (pid) => apiFetch(`/inventory/waste/${pid}`),
  createWaste: (data) => apiFetch("/inventory/waste/", { method: "POST", body: JSON.stringify(data) }),
  updateWaste: (id, data) => apiFetch(`/inventory/waste/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteWaste: (id) => apiFetch(`/inventory/waste/${id}`, { method: "DELETE" }),

  // Calculation
  calculate: (pid) => apiFetch(`/calculate/${pid}`),
  exportExcel: (pid) => `${API_BASE}/calculate/${pid}/export/excel`,
};

const LIFE_CYCLE_STAGES = [
  "Rohstoffbereitstellung & Vorverarbeitung",
  "Herstellung",
  "Transport & Lagerung (intern/Inbound)",
];

const SUB_CATEGORIES = [
  "Hauptmaterialgewinnung & Aufbereitung",
  "Hilfsstoffe (Druckfarben Additive Trennmittel etc.)",
  "Verpackung (Primär/Produkt)",
  "Verpackung (Transport/Logistik)",
  "Inbound Transport (LKW Schiff Bahn Luft)",
  "Innerbetrieblicher Transport (Stapler Lager)",
  "Strom (Netz/Mix)",
  "Strom (Erneuerbar/Grün)",
  "Wärme & Dampf (Gas/Öl/Biomasse)",
  "Direkte Prozessemissionen (Scope 1 / Kältemittel)",
  "Kläranlage & Abwasser",
  "Abfall Produktion",
  "Wartung und Pflege",
  "Maschinenteile",
];

function fmt(val, decimals = 4) {
  if (val === null || val === undefined) return "–";
  return Number(val).toFixed(decimals);
}

function showToast(msg, type = "success") {
  const toast = document.getElementById("toast");
  if (!toast) return;
  toast.textContent = msg;
  toast.className = `fixed bottom-6 right-6 px-5 py-3 rounded-lg text-white text-sm font-medium shadow-lg transition-all duration-300 ${
    type === "error" ? "bg-red-600" : "bg-green-600"
  }`;
  toast.style.opacity = "1";
  setTimeout(() => { toast.style.opacity = "0"; }, 3000);
}
