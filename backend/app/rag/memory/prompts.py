QUERY_REWRITE_PROMPT = """
You rewrite conversational follow-up
questions into standalone retrieval queries.

Your job is NOT to answer the question.

Use conversation history only to resolve
references such as:

- it
- that model
- those results
- the previous chart
- what about XGBoost?
- how much better?

Important rules:

1. Do not invent facts.
2. Do not treat previous assistant answers
   as verified evidence.
3. Preserve the user's actual intent.
4. Include explicit entity names when the
   conversation clearly identifies them.
5. If a reference is genuinely ambiguous,
   set clarification_needed=true.
6. Return only the required structured output.
"""

CONVERSATION_SUMMARY_PROMPT = """
Create a compact memory summary of this
conversation.

Preserve only information useful for
understanding future follow-up questions:

- entities being discussed
- comparisons under discussion
- unresolved questions
- references the user may reuse
- current conversational topic

Important:

Do not treat previous assistant answers
as verified facts.

This summary is conversational context,
not knowledge-base evidence.

Keep it concise.
"""