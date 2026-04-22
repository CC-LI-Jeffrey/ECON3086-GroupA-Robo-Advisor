# ECON3086 — Group A: Robo-Advisor Project

Welcome to the Group A Robo-Advisor project. 

This document explains how to run the app step by step, plus how we split work and module contracts.

---

## Step-by-step: run the app

### Step 1 — Open the project folder in a terminal

Change to the repository root (the folder that contains `app.py` and `requirements.txt`):

```bash
cd /path/to/ECON3086-GroupA-Robo-Advisor
```

### Step 2 —  Use a virtual environment (Recommended)

This keeps dependencies isolated from your system Python.

```bash
python3 -m venv .venv
source .venv/bin/activate    # macOS / Linux
# Windows: .venv\Scripts\activate
```

Skip this step if you already manage environments another way.

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

Wait until all packages finish installing without errors.

### Step 4 — Set the **HKBU GenAI API key**

#### A. Generate the API key (HKBU GenAI website)

1. **Open the URL** in your browser: [https://genai.hkbu.edu.hk](https://genai.hkbu.edu.hk)
2. Click the control in the **bottom-left corner** of the page (menu / account area).
3. Click **Profile and Settings**.
4. Click **API**.
5. Click **Generate API** to create a key.
6. **Copy the API key** and paste it into `.env` as described below (do not share the key in chat, screenshots, or git).

#### B. Put the key in `.env` (project root)

1. In the **project root**, create your local env file from the tracked example:
  ```bash
   cp .env.example .env
  ```
   On Windows PowerShell: `Copy-Item .env.example .env`
2. Open `.env`, set `HKBU_AI_API_KEY` to your copied key (no quotes unless required).
3. Start the app from the **same project root** so `python-dotenv` can load `.env`.

### Step 5 — Start Streamlit

From the project root:

```bash
streamlit run app.py
```

Your browser should open the app.

### Step 6 — Verify the AI connection (Optional)

After you set `HKBU_AI_API_KEY` in Step 4:

```bash
python _test_ai_live.py
```

If the key is missing, the script would tells you to set `HKBU_AI_API_KEY` in `.env`.

---

