VISUAL_ANALYSIS_PROMPT = """
You are analyzing a visual asset from a
retrieval-augmented generation system.

Inspect only what is visibly supported by
the image.

Return ONLY valid JSON using this schema:

{
  "visual_type": "chart | diagram | table |
                  screenshot | document_page |
                  photograph | other",

  "title": "visible title or null",

  "summary":
      "concise factual description",

  "visible_text": [
      "important visible labels"
  ],

  "key_values": [
      {
        "label": "name of metric or item",
        "value": "visible value or null",
        "unit": "unit or null"
      }
  ],

  "relationships": [
      "important comparisons or relationships"
  ],

  "uncertainties": [
      "anything unreadable or uncertain"
  ]
}

Rules:

1. Do not invent values.
2. Do not infer text that is unreadable.
3. If a value is uncertain, report it under
   uncertainties.
4. Do not add outside knowledge.
5. Describe only information supported by
   the image.
6. Return JSON only.
"""