import { useState } from "react";
import type { FormEvent } from "react";
import { createKnowledgeBase, deleteKnowledgeBase } from "../api/client";
import type { KnowledgeBase } from "../api/types";

interface Props {
  selected?: KnowledgeBase;
  disabled: boolean;
  onCreated: (kb: KnowledgeBase) => Promise<void>;
  onDeleted: (id: string) => Promise<void>;
  onBusyChange: (busy: boolean) => void;
}

export function KnowledgeBaseControls({selected, disabled, onCreated, onDeleted, onBusyChange}: Props) {
  const [showForm, setShowForm] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [description, setDescription] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function create(event: FormEvent) {
    event.preventDefault();
    if (busy || disabled) return;
    setBusy(true); onBusyChange(true); setError(null);
    try {
      const response = await createKnowledgeBase({name: name.trim(), slug: slug.trim(), description: description.trim() || null});
      setShowForm(false); setName(""); setSlug(""); setDescription("");
      await onCreated(response.data);
    } catch (err) { setError(err instanceof Error ? err.message : "Could not create knowledge base."); }
    finally { setBusy(false); onBusyChange(false); }
  }

  async function remove() {
    if (!selected || busy || disabled) return;
    setBusy(true); onBusyChange(true); setError(null);
    try {
      await deleteKnowledgeBase(selected.id);
      setConfirmDelete(false);
      await onDeleted(selected.id);
    } catch (err) { setError(err instanceof Error ? err.message : "Could not delete knowledge base."); }
    finally { setBusy(false); onBusyChange(false); }
  }

  return <div className="kb-controls">
    <button type="button" disabled={busy || disabled} onClick={() => {setShowForm(!showForm); setConfirmDelete(false); setError(null);}}>
      {showForm ? "Cancel creation" : "+ Create knowledge base"}
    </button>
    {showForm && <form className="kb-form" onSubmit={create}>
      <label>Name<input required minLength={2} maxLength={200} value={name} disabled={busy}
        onChange={event => {setName(event.target.value); setSlug(event.target.value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""));}} /></label>
      <label>Slug<input required minLength={2} maxLength={200} pattern="[a-z0-9]+(-[a-z0-9]+)*" value={slug} disabled={busy} onChange={event => setSlug(event.target.value)} /></label>
      <label>Description (optional)<textarea value={description} disabled={busy} onChange={event => setDescription(event.target.value)} /></label>
      <button disabled={busy || name.trim().length < 2 || slug.length < 2}>{busy ? "Creating..." : "Create"}</button>
    </form>}
    {selected && !showForm && <button type="button" className="danger-button" disabled={busy || disabled}
      onClick={() => {setConfirmDelete(true); setError(null);}}>Delete knowledge base</button>}
    {confirmDelete && selected && <div className="delete-confirmation" role="alert">
      <p>Delete <strong>{selected.name}</strong> and its documents and conversations? This cannot be undone.</p>
      <button type="button" className="danger-button" disabled={busy || disabled} onClick={remove}>{busy ? "Deleting..." : "Delete permanently"}</button>
      <button type="button" disabled={busy} onClick={() => setConfirmDelete(false)}>Cancel</button>
    </div>}
    {error && <p className="error-box" role="alert">{error}</p>}
  </div>;
}
