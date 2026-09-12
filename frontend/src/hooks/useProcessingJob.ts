import {
  useEffect,
  useState,
} from "react";

import {
  getProcessingJob,
} from "../api/client";

import type {
  ProcessingJob,
} from "../api/types";


export function useProcessingJob(
  jobId: string | null,
) {

  const [
    job,
    setJob,
  ] = useState<
    ProcessingJob | null
  >(
    null,
  );


  useEffect(() => {

    if (!jobId) {

      setJob(null);

      return;
    }


    let cancelled = false;

    let timer:
      number | undefined;


    async function poll() {

      try {

        const response =
          await getProcessingJob(
            jobId!,
          );


        if (cancelled) {
          return;
        }


        setJob(
          response.data
        );


        const finished =
          response.data.status
            === "succeeded"
          ||
          response.data.status
            === "failed";


        if (!finished) {

          timer =
            window.setTimeout(
              poll,
              2000,
            );
        }

      } catch {

        if (!cancelled) {

          timer =
            window.setTimeout(
              poll,
              3000,
            );
        }
      }
    }


    poll();


    return () => {

      cancelled = true;

      if (timer) {

        window.clearTimeout(
          timer
        );
      }
    };

  }, [jobId]);


  return job;
}