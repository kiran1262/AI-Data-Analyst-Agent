# 🤖 AI Data Analyst Agent

<p align="center">
  <strong>Upload data · Ask questions · Discover insights · Generate charts</strong>
</p>

An interactive, dark-neon analytics workspace built with **Python, Streamlit, Pandas, Plotly, Groq API and LangChain-compatible dependencies**. Upload your own CSV or Excel file, inspect its structure, ask questions in natural language and create interactive visualisations.

> **No sample dataset is included.** The application starts with an upload screen and analyses only the file you provide.

---

## ✨ Features

### 1. Upload your own data
- Upload `.csv`, `.xlsx` or `.xls` files.
- Read the uploaded file directly into Pandas.
- Detect numeric and categorical columns.
- No bundled sample dataset and no fixed banking/sales schema.

### 2. AI natural-language analyst
Ask questions such as:
- “Summarise this dataset in simple business language.”
- “Which fields have the most missing values?”
- “What are the main patterns I should investigate?”
- “Explain the distribution of the revenue column.”
- “What questions should a business stakeholder ask about this data?”

The app sends a compact dataset profile, aggregate statistics and a small preview of rows to Groq to ground the answer. It does **not** send the entire uploaded file to the LLM.

### 3. Interactive dashboard
- Neon dark theme inspired by futuristic AI analytics interfaces.
- KPI cards for rows, columns, duplicate rows and missing cells.
- Numeric distribution and category composition charts.
- Automatic column profile and data-quality overview.

### 4. Chart Studio
Create interactive Plotly:
- Bar charts
- Line charts
- Scatter plots
- Histograms
- Pie charts
- Box plots

Choose X-axis, Y-axis and optional colour grouping.

### 5. Data quality and extraction
- Preview uploaded data.
- Inspect data types, missing values and unique counts.
- Download the analysed data as CSV.
- Download a data quality report as CSV.

---

## 🧰 Technology stack

| Technology | Purpose |
|---|---|
| Python | Application logic and data processing |
| Streamlit | Interactive web dashboard |
| Pandas | Data loading, cleaning and analysis |
| NumPy | Numerical operations |
| Plotly Express | Interactive charts |
| Groq API | Fast LLM responses |
| LangChain / langchain-groq | Installed integration layer for extending the agent |
| openpyxl / xlrd | Excel file reading |

**Implementation note:** The current chat uses the official Groq Python SDK directly for a simple, transparent API call. LangChain packages are included so you can extend the workflow with chains, prompts, tools or agents without changing the core upload and charting workflow.

---

## 🔑 Groq API key — free developer access

Groq offers a developer console where you can create an API key. Access, rate limits, model availability and free usage policies can change, so check the current terms in your Groq account.

1. Open [Groq Console](https://console.groq.com/).
2. Create an account or sign in.
3. Open the API Keys section.
4. Create a new API key and copy it securely.
5. In this app, paste the key into **Groq API key** in the left sidebar.

Official quickstart: https://console.groq.com/docs/quickstart  
Current models and model IDs: https://console.groq.com/docs/models

### Configure the key locally (recommended)

Create a file named `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "paste_your_groq_api_key_here"
```

The app reads this secret automatically. This file is ignored by Git via `.gitignore`. Never put your real API key in `app.py`, README, screenshots, public repositories or committed config files.

Alternative: paste your key into the password field in the app sidebar for the current session.

### Model selection

The sidebar lets you choose a model ID. The default is `llama-3.3-70b-versatile`. Groq's available model list can change; if a model is unavailable, select a currently supported model from the official model catalogue.

---

## 🚀 Run locally on Windows

### Step 1 — Install Python and Git
Install a current Python 3 version and Git for Windows if they are not already installed.

- Python: https://www.python.org/downloads/
- Git: https://git-scm.com/downloads

### Step 2 — Open the project folder
Extract the ZIP file, open the `ai_data_analyst_agent` folder, then open PowerShell in that folder.

### Step 3 — Create and activate a virtual environment

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### Step 4 — Install dependencies

```powershell
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

### Step 5 — Add your Groq key
Create `.streamlit/secrets.toml` as described above, or paste the key into the app sidebar after launch.

### Step 6 — Start the dashboard

```powershell
py -m streamlit run app.py
```

Streamlit will display a local URL, usually `http://localhost:8501`.

---

## 📁 Project structure

```text
ai_data_analyst_agent/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── .streamlit/
    └── secrets.toml.example
```

No datasets are stored in this repository. The `.streamlit/secrets.toml` file is created locally by you and is excluded from Git.

---

## ☁️ Deploy on Streamlit Community Cloud

1. Push this project to a GitHub repository.
2. Visit https://share.streamlit.io/ and sign in with GitHub.
3. Choose **Create app**.
4. Select your repository and `main` branch.
5. Set the main file path to `app.py`.
6. Open **Advanced settings → Secrets**.
7. Add your secret in TOML format:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

8. Deploy the app.

Do not add the key to GitHub repository files or commit history. Set it in Streamlit's Secrets settings.

---

## 🔒 Privacy, security and limitations

- The application does not bundle or retain a sample dataset.
- Uploaded data is held in the active Streamlit session; deployment hosts may have their own logging, session and storage behaviour.
- A dataset profile, aggregate statistics and up to six preview rows are sent to Groq when you ask an AI question. Do not use confidential or personally identifiable information unless you have appropriate approval and have reviewed the provider's terms.
- The entire file is not sent to Groq by this implementation.
- Never upload passwords, API keys, payment card data, government identifiers or sensitive customer records.
- The AI answer is generated from a limited profile and preview. It may not be able to answer exact questions requiring a full-dataset calculation. Verify important figures in Pandas, SQL or Power BI.
- This is an analytics assistant, not an autonomous financial, legal, medical or compliance decision system.
- Groq API access and rate limits depend on the account, model and current provider policy.

---

## 🧭 Suggested future enhancements

- Safe, deterministic Pandas query tools for exact calculations.
- SQL database connectors (SQLite, PostgreSQL, MySQL).
- LangChain tool-calling agent with explicit allow-listed operations.
- Automated EDA report export to PDF.
- Dashboard filters and cross-filtering.
- Multi-file comparison and data joins.
- Role-based access, authentication and audit logging.

---

## 🧪 Troubleshooting

**`ModuleNotFoundError`**
```powershell
py -m pip install -r requirements.txt
```

**Groq authentication error**
- Confirm the API key is copied correctly.
- Ensure there are no extra spaces or quote characters in the sidebar input.
- Check that the key is active in Groq Console.

**Model not found / unavailable**
- Open https://console.groq.com/docs/models.
- Select a currently available model ID in the sidebar.

**Excel file error**
- Confirm the file is a valid `.xlsx` or `.xls`.
- Close the workbook in Excel and try uploading again.

**Large upload or slow response**
- Try a smaller file or remove unnecessary columns.
- The app limits the LLM context to a profile and a few preview rows, but large files can still take longer to load and profile.

---

## 📌 GitHub repository description

AI Data Analyst Agent built with Python, Streamlit, Pandas, Plotly and Groq. Upload CSV/Excel files, ask natural-language questions, explore data quality and generate interactive charts in a futuristic analytics dashboard.

## 🏷️ Suggested GitHub topics

`ai-data-analyst` `data-analysis` `generative-ai` `groq` `llm` `langchain` `python` `pandas` `streamlit` `plotly` `data-visualization` `eda`

---

## 📄 License

Choose and add a license before accepting external contributions or distributing this project. If you add one, update this section accordingly.
