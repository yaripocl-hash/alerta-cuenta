FRAUD_TYPES = [
    "phishing",
    "vishing",
    "smishing",
    "whatsapp_impersonation",
    "deceptive_transfer",
    "fake_online_purchase",
    "unauthorized_account_access",
    "other",
]

CASE_STATUSES = ["draft", "submitted", "in_review", "closed"]

ALLOWED_EVIDENCE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
    "text/plain",
}

MAX_EVIDENCE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

TARGET_INSTITUTIONS = ["bank", "fintech", "sernac", "cmf", "csirt", "pdi", "other"]
