# Gemini Interactive Chat (Python)

This project provides a simple interactive chat script using Google's **GenAI SDK**.  
It supports two modes:

- **Gemini API (Developer Mode)** – using an API key  
- **Vertex AI (Enterprise Mode)** – using Google Cloud authentication  

---

## Prerequisites

- Python 3.9+
- pip installed
- A Google account

---

## Project Setup

### 1. Clone the repo
```bash
git clone https://github.com/owhere/ivertex.git
cd ivertex
```
---

### 2. Install dependencies

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```
---

### 3. Create a `.env` file or set envs

Create a file named `.env` in your project root . (Local testing)

```bash
cp cli/example.env .env
```

#### Option A: Gemini API (Simplest)

```env
GOOGLE_GENAI_USE_VERTEXAI=False
GOOGLE_API_KEY=your_api_key_here 
```
Get your API key from Google AI Studio.
---

#### Option B: Vertex AI (Enterprise / GCP)

```env
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1
```

Then authenticate:

```bash
gcloud auth application-default login
```

---

## How the Script Works

- Reads environment variables from `.env`
- Determines whether to use:
  - API key (Gemini API), or
  - GCP authentication (Vertex AI)
- Initializes the GenAI client
- Starts a **stateful chat session**
- Keeps conversation history automatically

---

## Run the Script

```bash
python cli/api_call.py
```
---

## Usage

Once running, you’ll see:

```
--- Successfully connected via: Vertex AI ---
--- Project ID: your_project_id | Location: us-central1 ---
Gemini Interactive Chat (Type 'exit' or 'quit' to stop)
```

Example:

```
You: Hello
Gemini: Hi! How can I help you today?
```

To exit:

```
exit
```
