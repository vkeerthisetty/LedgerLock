"use strict";

const GENESIS_HASH = "0".repeat(64);
const state = { records: [], lastVerification: null };
const apiMode = document.documentElement.dataset.apiMode || "mock";

const elements = {
  form: document.querySelector("#event-form"),
  formError: document.querySelector("#form-error"),
  ledgerBody: document.querySelector("#ledger-body"),
  ledgerEmpty: document.querySelector("#ledger-empty"),
  ledgerMessage: document.querySelector("#ledger-message"),
  recordCount: document.querySelector("#record-count"),
  latestSequence: document.querySelector("#latest-sequence"),
  chainStatus: document.querySelector("#chain-status"),
  checkpointStatus: document.querySelector("#checkpoint-status"),
  verificationEmpty: document.querySelector("#verification-empty"),
  verificationResult: document.querySelector("#verification-result"),
  verificationTitle: document.querySelector("#verification-title"),
  verificationMessage: document.querySelector("#verification-message"),
  checkedRecords: document.querySelector("#checked-records"),
  failedSequence: document.querySelector("#failed-sequence"),
  checkedAt: document.querySelector("#checked-at"),
  mockWarning: document.querySelector("#mock-warning"),
  demoControls: document.querySelector("#demo-controls"),
  toast: document.querySelector("#toast"),
};

function canonicalRecord(record) {
  return JSON.stringify({
    sequence: record.sequence,
    timestamp: record.timestamp,
    event_type: record.event_type,
    actor_id: record.actor_id,
    action: record.action,
    resource_id: record.resource_id,
    outcome: record.outcome,
    previous_hash: record.previous_hash,
  });
}

async function sha256(value) {
  const bytes = new TextEncoder().encode(value);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

class MockLedgerApi {
  async listRecords() { return structuredClone(state.records); }

  async createEvent(payload) {
    const previous = state.records.at(-1);
    const record = {
      sequence: previous ? previous.sequence + 1 : 1,
      timestamp: new Date().toISOString(),
      ...payload,
      previous_hash: previous ? previous.current_hash : GENESIS_HASH,
    };
    record.current_hash = await sha256(canonicalRecord(record));
    state.records.push(record);
    return structuredClone(record);
  }

  async verify() {
    for (let index = 0; index < state.records.length; index += 1) {
      const record = state.records[index];
      const expectedSequence = index + 1;
      const expectedPreviousHash = index === 0 ? GENESIS_HASH : state.records[index - 1].current_hash;
      const expectedCurrentHash = await sha256(canonicalRecord(record));
      if (record.sequence !== expectedSequence || record.previous_hash !== expectedPreviousHash || record.current_hash !== expectedCurrentHash) {
        return { valid: false, checked_records: index + 1, failed_sequence: record.sequence, message: "The disposable demo chain no longer matches its stored hashes." };
      }
    }
    return { valid: true, checked_records: state.records.length, failed_sequence: null, message: "The disposable demo chain is internally consistent." };
  }

  async tamper() {
    if (!state.records.length) throw new Error("Create at least one demo record before tampering.");
    state.records[0].action = `${state.records[0].action} (changed)`;
  }

  async reset() { state.records = []; state.lastVerification = null; }
}

class LiveLedgerApi {
  async request(path, options = {}) {
    const response = await fetch(path, {
      ...options,
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.message || body.detail || "The LedgerLock service could not complete the request.");
    return body;
  }

  async listRecords() { return this.request("/api/ledger"); }
  async createEvent(payload) { return this.request("/api/events", { method: "POST", body: JSON.stringify(payload) }); }
  async verify() { return this.request("/api/verify", { method: "POST" }); }
}

const api = apiMode === "mock" ? new MockLedgerApi() : new LiveLedgerApi();

function shortHash(hash) { return hash ? `${hash.slice(0, 9)}…${hash.slice(-6)}` : "—"; }
function escapeText(value) { const span = document.createElement("span"); span.textContent = String(value); return span.innerHTML; }

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.hidden = false;
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => { elements.toast.hidden = true; }, 3200);
}

function setBusy(button, busy, label) {
  button.disabled = busy;
  if (!button.dataset.defaultLabel) button.dataset.defaultLabel = button.textContent;
  button.textContent = busy ? label : button.dataset.defaultLabel;
}

function renderLedger(records) {
  state.records = records;
  elements.ledgerBody.innerHTML = records.map((record) => `
    <tr>
      <td><strong>${escapeText(record.sequence)}</strong></td>
      <td>${escapeText(new Date(record.timestamp).toLocaleString())}</td>
      <td>${escapeText(record.event_type)}</td>
      <td>${escapeText(record.actor_id)}</td>
      <td>${escapeText(record.outcome)}</td>
      <td><code title="${escapeText(record.previous_hash)}">${escapeText(shortHash(record.previous_hash))}</code></td>
      <td><code title="${escapeText(record.current_hash)}">${escapeText(shortHash(record.current_hash))}</code></td>
    </tr>`).join("");
  elements.ledgerEmpty.hidden = records.length > 0;
  elements.recordCount.textContent = String(records.length);
  elements.latestSequence.textContent = records.length ? String(records.at(-1).sequence) : "—";
  elements.ledgerMessage.textContent = records.length ? `${records.length} synthetic record${records.length === 1 ? "" : "s"}` : "";
}

function renderVerification(result) {
  state.lastVerification = result;
  elements.verificationEmpty.hidden = true;
  elements.verificationResult.hidden = false;
  elements.verificationResult.classList.toggle("is-invalid", !result.valid);
  elements.verificationTitle.textContent = result.valid ? "Chain verified" : "Tampering detected";
  elements.verificationMessage.textContent = result.message;
  elements.checkedRecords.textContent = String(result.checked_records);
  elements.failedSequence.textContent = result.failed_sequence ?? "—";
  elements.checkedAt.textContent = new Date().toLocaleTimeString();
  elements.chainStatus.textContent = result.valid ? "Valid" : "Tamper detected";
  elements.chainStatus.className = `status-pill ${result.valid ? "status-valid" : "status-invalid"}`;
  elements.checkpointStatus.textContent = apiMode === "mock" ? "Not tested" : (result.checkpoint_valid ? "Verified" : "Unavailable");
  elements.checkpointStatus.className = `status-pill ${result.checkpoint_valid ? "status-valid" : "status-neutral"}`;
}

function readForm() {
  const payload = Object.fromEntries(new FormData(elements.form));
  const invalid = [...elements.form.elements].filter((field) => field.required && !String(field.value).trim());
  [...elements.form.elements].forEach((field) => field.removeAttribute?.("aria-invalid"));
  invalid.forEach((field) => field.setAttribute("aria-invalid", "true"));
  if (invalid.length) throw new Error("Complete every required field using synthetic values.");
  return Object.fromEntries(Object.entries(payload).map(([key, value]) => [key, String(value).trim()]));
}

async function refreshLedger() {
  const records = await api.listRecords();
  renderLedger(Array.isArray(records) ? records : records.records || []);
}

elements.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  elements.formError.hidden = true;
  const button = elements.form.querySelector("button[type='submit']");
  try {
    const payload = readForm();
    setBusy(button, true, "Creating…");
    await api.createEvent(payload);
    await refreshLedger();
    elements.form.reset();
    showToast("Synthetic audit event created.");
  } catch (error) {
    elements.formError.textContent = error.message;
    elements.formError.hidden = false;
  } finally {
    setBusy(button, false, "Creating…");
  }
});

document.querySelector("#verify-button").addEventListener("click", async (event) => {
  try {
    setBusy(event.currentTarget, true, "Verifying…");
    renderVerification(await api.verify());
  } catch (error) { showToast(error.message); }
  finally { setBusy(event.currentTarget, false, "Verifying…"); }
});

document.querySelector("#refresh-button").addEventListener("click", () => refreshLedger().catch((error) => showToast(error.message)));

if (apiMode === "mock") {
  elements.mockWarning.hidden = false;
  elements.demoControls.hidden = false;
  document.querySelector("#tamper-button").addEventListener("click", async () => {
    try { await api.tamper(); await refreshLedger(); showToast("Disposable demo record changed. Run verification again."); }
    catch (error) { showToast(error.message); }
  });
  document.querySelector("#reset-data-button").addEventListener("click", async () => {
    await api.reset();
    await refreshLedger();
    elements.verificationEmpty.hidden = false;
    elements.verificationResult.hidden = true;
    elements.chainStatus.textContent = "Not checked";
    elements.chainStatus.className = "status-pill status-neutral";
    showToast("Disposable demo data reset.");
  });
}

refreshLedger().catch((error) => showToast(error.message));
