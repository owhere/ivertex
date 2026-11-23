# Using Gemini API via Vertex AI with CLI and SDK

## 1. Enterprise Use

To ensure compliance with data protection requirements and secure access
control, we have enforced the following policy on Gemini API usage:

-   **Vertex AI only**: All Gemini API usage must go through Vertex AI.
-   **No direct Gemini API keys**: Direct access via public Gemini
    endpoints is not permitted.
-   **SSO Enforcement**: Access must be authenticated via organisational
    SSO (Entra ID / Google Cloud IAM federation).

## 2. Prerequisites

Before using Gemini via Vertex AI, ensure the following:

-   **Access to a GCP Project**
    You must have access to a Google Cloud project.

-   **Verify Your Project in the Google Cloud Console**
    Once your project has been provisioned, confirm access via the
    Google Cloud Console:  [https://console.cloud.google.com/](https://console.cloud.google.com/)

    -   Sign in using your University SSO account
        (e.g. `abcd1234@ox.ac.uk`)
    -   Open the **Project Selector** (top-left, next to the *Google
        Cloud* logo)
    -   At **All** tab, navigate through

        `No organisation → Your Group → Development → Your Project`

        Please get yourself familar with Project number (12 digits) and Project ID (a connected string prefixed with ox)

    -   Go to **APIs & Services** to review enabled APIs and monitor usage later. The **Agent Platform API** is enabled for you to access Gemini models through Vertex AI APIs.

-   **Install the gcloud CLI**

    Following the official guide:, install the [Google Cloud SDK](https://docs.cloud.google.com/sdk/docs/install-sdk).


-   **Authenticate and Set Your Project**

    After installation, verify access from your terminal:

```bash
gcloud auth login
gcloud auth login --no-launch-browser # if using a remote host
```

You then complete the organisational SSO flow from your local browser.
- When prompted: Google Cloud SDK wants to access your Google Account, allow it.
- Then you should see: You are now authenticated with the gcloud CLI!

In your terminal, set your project.

``` bash
gcloud config set project <PROJECT_ID>
```

This ensures you are authenticated via SSO and working in the correct project.

-   **Validate Access**

Run the following command to confirm you can access the project:

```bash
gcloud projects describe <PROJECT_ID>
```

If successful, this will return project metadata. If not, check your permissions or authentication.

## 3. Access via Gemini CLI with ADC

**Application Default Credentials (ADC)** is how the CLI authenticates without needing a service account key file sitting on disk.

### 3.1 Install CLI

Install the Gemini CLI

``` bash
npm install -g @google/gemini-cli # sudo if needed
```

### 3.2 Prepare the environment

``` bash
mkdir -p ~/.gemini
vim ~/.gemini/.env
```

In the file setting up those variables
```bash
$ cat .env
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=YOUR-PROJECT-ID
export GOOGLE_CLOUD_LOCATION=global
```

### 3.3 Make sure to unset API key

Please unset following keys as they take precedence and prevent ADC from working

``` bash
unset GOOGLE_API_KEY
unset GEMINI_API_KEY
```

### 3.4 Authenticate

``` bash
gcloud auth application-default login
```
or following if on a remote host
```bash
gcloud auth application-default login  --no-launch-browser
```

You then complete the organisational SSO flow from your local browser.
- When prompted: Google Auth Library wants additional access to your Google Account, select all to allow Google Auth Library access your account, and continue.
- Then you should see: You are now authenticated with the gcloud CLI!

### 3.5 Run gemini

```bash
source ~/.gemini/.env
gemini
```
use **/auth**, select Vertex AI and use **/model**, select a model. Following models are available at the time of update:

1. gemini-3.1-pro-preview
2. gemini-3-flash-preview
3. gemini-3.1-flash-lite-preview
4. gemini-2.5-pro
5. gemini-2.5-flash
6. gemini-2.5-flash-lite

### 3.6 Diagnosis

Sometime, the authentication failed due to caching. Run following to clear the cache

```bash
gcloud auth application-default revoke
```
or
```
rm ~/.config/gcloud/application_default_credentials.json
```

## 4. Access via Python SDK

Please follow [Google Introduction to the Agent Platform SDK for Python](https://docs.cloud.google.com/gemini-enterprise-agent-platform/machine-learning/python-sdk/use-vertex-ai-python-sdk-ref) for SDK access.

