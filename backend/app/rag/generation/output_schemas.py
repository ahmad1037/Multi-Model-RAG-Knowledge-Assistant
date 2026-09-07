GROUNDED_ANSWER_SCHEMA = {
    "type": "object",

    "properties": {

        "answerable": {
            "type": "boolean",
        },

        "answer": {
            "type": "string",
        },

        "citations": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },

        "refusal_reason": {
            "type": "string",
        },
    },

    "required": [
        "answerable",
        "answer",
        "citations",
        "refusal_reason",
    ],

    "additionalProperties": False,
}


GROUNDING_VERIFICATION_SCHEMA = {
    "type": "object",

    "properties": {

        "all_claims_supported": {
            "type": "boolean",
        },

        "unsupported_claims": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },

        "supporting_source_ids": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },

        "explanation": {
            "type": "string",
        },
    },

    "required": [
        "all_claims_supported",
        "unsupported_claims",
        "supporting_source_ids",
        "explanation",
    ],

    "additionalProperties": False,
}