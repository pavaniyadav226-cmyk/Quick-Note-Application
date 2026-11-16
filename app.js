const form = document.getElementById("note-form");
const input = document.getElementById("note-input");
const saveBtn = document.getElementById("save-btn");
const errorEl = document.getElementById("error");
const listEl = document.getElementById("notes");
const emptyEl = document.getElementById("empty");
const counterEl = document.getElementById("counter");

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.hidden = !msg;
}

async function api(path, options) {
  const res = await fetch(path, options);
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Request failed.");
  return data;
}

function renderNote(note) {
  const li = document.createElement("li");
  li.dataset.id = note.id;

  const text = document.createElement("p");
  text.className = "note-text";
  text.textContent = note.content; // textContent, never innerHTML: prevents XSS

  const meta = document.createElement("div");
  meta.className = "note-meta";

  const time = document.createElement("time");
  time.dateTime = note.created_at;
  time.textContent = new Date(note.created_at).toLocaleString();

  const del = document.createElement("button");
  del.type = "button";
  del.className = "link";
  del.textContent = "Delete";
  del.addEventListener("click", () => deleteNote(note.id));

  meta.append(time, del);
  li.append(text, meta);
  return li;
}

function updateEmpty() {
  emptyEl.hidden = listEl.children.length > 0;
}

async function loadNotes() {
  try {
    const notes = await api("/api/notes");
    listEl.replaceChildren(...notes.map(renderNote));
    updateEmpty();
  } catch (err) {
    showError("Couldn't load notes: " + err.message);
  }
}

async function deleteNote(id) {
  try {
    await api(`/api/notes/${id}`, { method: "DELETE" });
    listEl.querySelector(`li[data-id="${id}"]`)?.remove();
    updateEmpty();
  } catch (err) {
    showError(err.message);
  }
}

input.addEventListener("input", () => {
  counterEl.textContent = `${input.value.length} / ${input.maxLength}`;
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  showError("");
  const content = input.value.trim();
  if (!content) return showError("Note can't be empty.");

  saveBtn.disabled = true;
  try {
    const note = await api("/api/notes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content }),
    });
    listEl.prepend(renderNote(note));
    input.value = "";
    counterEl.textContent = `0 / ${input.maxLength}`;
    updateEmpty();
    input.focus();
  } catch (err) {
    showError(err.message);
  } finally {
    saveBtn.disabled = false;
  }
});

loadNotes();