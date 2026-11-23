# GCP Text-to-Speech (Cloud TTS & Vertex AI) – User Onboarding Guide

Your GCP project (`<YOUR_PROJECT_ID>`) is configured and ready for Text-to-Speech workloads. Your group has been granted the required IAM permissions (`roles/serviceusage.serviceUsageConsumer` and `roles/aiplatform.user`), so you can begin integrating immediately.

---

## 1. Authentication Policy (No API Keys)

Per security guidelines, **do not create or use static API keys or JSON service account key files.** Both endpoints use keyless IAM authentication via Application Default Credentials (ADC):

* **Local Development:** Run the following commands once in your terminal to authenticate with your corporate identity and set the quota project:
  ```bash
  gcloud auth application-default login
  gcloud auth application-default set-quota-project <YOUR_PROJECT_ID>
  ```
* **Deployed Workloads (Cloud Run, GKE, Compute Engine):** Attach your workload's designated Service Account; ADC will authenticate automatically.

---

## 2. Choosing Which API to Use

Both APIs are enabled on the project and support Gemini-TTS models (`gemini-2.5-pro-tts`, `gemini-2.5-flash-tts`) as well as prebuilt voices such as `Kore`:

* **Use the Cloud Text-to-Speech API (`google-cloud-texttospeech`)** if you need:
  * Standard, Neural2, or Chirp 3 HD voices, or strict **SSML** pronunciation and timing control.
  * **Bidirectional streaming** (e.g., real-time conversational voice agents).
  * EU multi-region data residency via `eu-texttospeech.googleapis.com`.
* **Use the Vertex AI / Gen AI SDK (`google-genai`)** if you are:
  * Already calling Gemini models via `generateContent` and want a single unified SDK and schema.
  * Using single-region European endpoints (e.g., `europe-west2`) with prompt-driven speech synthesis.

---

## 3. Environment Configuration (`.env`)

> **Important:** Ensure `GEMINI_API_KEY` and `GOOGLE_API_KEY` are **unset** in your environment so the SDKs default to IAM authentication.

### Option A: Vertex AI (`google-genai` SDK)

```env
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=<YOUR_PROJECT_ID>
GOOGLE_CLOUD_LOCATION=eu

GEMINI_TTS_MODEL=gemini-2.5-pro-tts
GEMINI_TTS_VOICE=Kore
```

### Option B: Cloud Text-to-Speech (`google-cloud-texttospeech` SDK)

```env
GOOGLE_CLOUD_PROJECT=<YOUR_PROJECT_ID>
GEMINI_TTS_MODEL=gemini-2.5-pro-tts
GEMINI_TTS_VOICE=Kore
```

*(Note: The `google-cloud-texttospeech` SDK does not read `GOOGLE_CLOUD_LOCATION` automatically—pass `api_endpoint="eu-texttospeech.googleapis.com"` in `ClientOptions` when initializing your client to enforce EU routing.)*

---

## 4. Troubleshooting & Quick Verification

If you encounter a `403 PERMISSION_DENIED` or quota error on your first run:

1. Confirm you are signed into `gcloud` with your SSO account:
   ```bash
   gcloud auth list
   ```
2. Verify that your ADC quota project is set to `<YOUR_PROJECT_ID>`:
   ```bash
   gcloud auth application-default set-quota-project <YOUR_PROJECT_ID>
   ```
