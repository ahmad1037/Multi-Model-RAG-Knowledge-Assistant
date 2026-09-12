import {
  useEffect,
  useRef,
  useState,
} from "react";
import type {
  ChangeEvent,
} from "react";

import {
  getDocuments,
  getProcessingJob,
  uploadDocument,
} from "../api/client";
import type {
  DocumentItem,
  ProcessingJob,
} from "../api/types";

interface Props {
  knowledgeBaseId: string | null;
}

const TERMINAL_JOB_STATUSES = new Set([
  "completed",
  "failed",
  "succeeded",
]);

export function DocumentPanel({
  knowledgeBaseId,
}: Props) {
  const fileInputRef =
    useRef<HTMLInputElement>(null);
  const [documents, setDocuments] =
    useState<DocumentItem[]>([]);
  const [job, setJob] =
    useState<ProcessingJob | null>(null);
  const [isUploading, setIsUploading] =
    useState(false);
  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    setJob(null);
    setError(null);

    if (!knowledgeBaseId) {
      setDocuments([]);
      return;
    }

    let cancelled = false;

    void getDocuments(knowledgeBaseId)
      .then((response) => {
        if (!cancelled) {
          setDocuments(response.data);
        }
      })
      .catch((reason: unknown) => {
        if (!cancelled) {
          setError(
            reason instanceof Error
              ? reason.message
              : "Could not load documents.",
          );
        }
      });

    return () => {
      cancelled = true;
    };
  }, [knowledgeBaseId]);

  useEffect(() => {
    if (
      !job
      || TERMINAL_JOB_STATUSES.has(
        job.status.toLowerCase(),
      )
    ) {
      return;
    }

    const timer = window.setInterval(() => {
      void getProcessingJob(job.id)
        .then((response) => {
          const nextJob = response.data;
          setJob(nextJob);

          if (
            knowledgeBaseId
            && TERMINAL_JOB_STATUSES.has(
              nextJob.status.toLowerCase(),
            )
          ) {
            void getDocuments(knowledgeBaseId)
              .then((documentsResponse) => {
                setDocuments(
                  documentsResponse.data,
                );
              });
          }
        })
        .catch((reason: unknown) => {
          setError(
            reason instanceof Error
              ? reason.message
              : "Could not refresh processing progress.",
          );
        });
    }, 1500);

    return () => {
      window.clearInterval(timer);
    };
  }, [job, knowledgeBaseId]);

  async function handleFileChange(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    const file = event.target.files?.[0];

    if (!knowledgeBaseId || !file) {
      return;
    }

    setIsUploading(true);
    setJob(null);
    setError(null);

    try {
      const response = await uploadDocument(
        knowledgeBaseId,
        file,
      );
      const result = response.data;

      setDocuments((current) => [
        result.document,
        ...current.filter(
          (document) =>
            document.id !== result.document.id,
        ),
      ]);
      setJob(result.processing_job);
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Document upload failed.",
      );
    } finally {
      setIsUploading(false);
      event.target.value = "";
    }
  }

  return (
    <section
      className="document-panel"
      aria-labelledby="documents-heading"
    >
      <div className="document-panel__heading">
        <h2 id="documents-heading">
          Documents
        </h2>

        <button
          type="button"
          className="document-upload-button"
          disabled={
            !knowledgeBaseId || isUploading
          }
          onClick={() =>
            fileInputRef.current?.click()
          }
        >
          {isUploading ? "Uploading..." : "Upload"}
        </button>

        <input
          ref={fileInputRef}
          className="visually-hidden"
          type="file"
          onChange={handleFileChange}
          disabled={
            !knowledgeBaseId || isUploading
          }
        />
      </div>

      {isUploading && !job && (
        <div
          className="processing-status"
          role="status"
        >
          <strong>Uploading...</strong>
          <progress />
        </div>
      )}

      {job && (
        <div
          className="processing-status"
          role="status"
          aria-live="polite"
        >
          <div className="processing-status__header">
            <strong>{job.current_stage}</strong>
            <span>{job.progress_percent}%</span>
          </div>

          <progress
            value={job.progress_percent}
            max={100}
            aria-label={
              `${job.current_stage}: ${job.progress_percent}%`
            }
          />

          {job.status === "failed" && (
            <p className="error-box">
              {job.error_message
                ?? "Document processing failed."}
            </p>
          )}
        </div>
      )}

      {error && (
        <p className="error-box" role="alert">
          {error}
        </p>
      )}

      {documents.length === 0 ? (
        <p className="document-panel__empty">
          No documents uploaded yet.
        </p>
      ) : (
        <ul className="document-list">
          {documents.map((document) => (
            <li key={document.id}>
              <span>{document.original_filename}</span>
              <small>{document.status}</small>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
