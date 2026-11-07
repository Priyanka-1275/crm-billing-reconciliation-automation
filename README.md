# CRM Billing Reconciliation Automation

A Python-based CRM billing reconciliation and account-matching tool designed to identify potential mismatches between website facility records and CRM account records, organize review proposals, and support human-verified decisions through a web dashboard.

## 📌 Problem Statement

Organizations may maintain facility information across multiple systems, such as public websites and CRM platforms. Differences in facility names, locations, account relationships, and billing records can make manual reconciliation time-consuming and error-prone.

This project addresses that challenge by automating the initial comparison process, identifying potential matches and duplicates, and presenting uncertain cases for manual review before any account-related decision is made.

## ✨ Key Features

- **Website Data Extraction:** Collects facility information from website pages.
- **Data Cleaning:** Standardizes and prepares extracted records for comparison.
- **CRM Data Analysis:** Inspects CRM account information and relevant account relationships.
- **Automated Account Matching:** Compares website facilities with CRM accounts using matching logic.
- **Duplicate Detection:** Identifies possible duplicate accounts and overlapping records.
- **Match Classification:** Categorizes results into match categories, including exact matches, multiple candidates, and unmatched records.
- **Review Queue Generation:** Creates structured proposals for records that require further verification.
- **Interactive Review Dashboard:** Provides a web interface to inspect reconciliation results and review proposals.
- **Human-in-the-Loop Approval:** Supports approval or rejection decisions with ownership verification.
- **Audit Logging:** Records review decisions for traceability.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Data processing, matching, and automation |
| Flask | Backend web application and API endpoints |
| HTML | Dashboard structure |
| CSS | Dashboard styling |
| JavaScript | Dashboard interactions |
| JSON | Data storage and exchange |
| Git & GitHub | Version control and project hosting |

## 🔄 Project Workflow

1. **Website Data Collection**  
   Extract facility details from the relevant website.

2. **Data Cleaning and Preparation**  
   Normalize and clean the collected website information.

3. **CRM Data Inspection**  
   Analyze CRM account records, account IDs, parent relationships, and relevant billing information.

4. **Record Matching**  
   Compare website facilities against CRM records using matching and comparison scripts.

5. **Match Classification**  
   Identify exact matches, ambiguous matches, potential duplicates, and unmatched facilities.

6. **Review Queue Creation**  
   Generate structured proposals for cases requiring manual verification.

7. **Dashboard Review**  
   Display proposals through the Flask-powered dashboard.

8. **Decision and Audit Trail**  
   Allow reviewers to approve or reject proposals, record verification decisions, and maintain an audit log.

## 📂 Project Structure

```text
crm-billing-reconciliation-automation/
│
├── app.py
├── analyze_crm.py
├── build_review_queue.py
├── clean_website_data.py
├── compare_owosso.py
├── compare_website_crm.py
├── improved_matching.py
├── improved_matching_backup.py
├── initial_matching.py
├── inspect_ambiguous.py
├── inspect_bellhaven_children.py
├── inspect_city_matches.py
├── inspect_crm.py
├── inspect_duplicates.py
├── inspect_kettering_parents.py
├── inspect_match_categories.py
├── inspect_review.py
├── inspect_strong.py
├── inspect_unmatched_and_partial_matches.py
├── inspect_unmatched_website.py
├── investigate_kettering.py
├── validate_website_data.py
│
├── templates/
│   └── index.html
│
├── verification/
│   ├── verify_api.py
│   └── verify_website.py
│
└── .gitignore
```

## ⚙️ Setup and Installation

### Prerequisites

- Python 3.9 or later
- Git
- pip

### 1. Clone the repository

```bash
git clone https://github.com/Priyanka-1275/crm-billing-reconciliation-automation.git
```

### 2. Navigate to the project directory

```bash
cd crm-billing-reconciliation-automation
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows:**

```powershell
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

### 4. Install dependencies

Install Flask:

```bash
pip install Flask
```

Install any additional dependencies required by the individual scripts.

### 5. Configure API credentials

If using the CRM verification script, configure the required API token as an environment variable.

**PowerShell:**

```powershell
$env:CRM_API_TOKEN="your_api_token"
```

Do not commit API tokens, credentials, or private CRM data to GitHub.

### 6. Run the application

```bash
python app.py
```

Open the following address in your browser:

```text
http://127.0.0.1:5000
```

## 🔐 Data Security and Review

- Generated CRM snapshots and intermediate data files are excluded from version control.
- API credentials are supplied through environment variables.
- Account-related proposals are intended for human review.
- Approval or rejection in the review dashboard records a decision; it does not automatically update the external CRM.

**Note:** The dashboard is intended for local review and development. Authentication and appropriate access controls should be implemented before any public deployment.

## 🎯 Project Objective

The objective of this project is to reduce manual effort in CRM billing reconciliation by combining automated data extraction, record comparison, duplicate identification, structured review proposals, and human-verified decision tracking.

## 👩‍💻 Author

**Tejaswini Kothapalli**

GitHub: [Priyanka-1275](https://github.com/Priyanka-1275)

---

*Built to make CRM account reconciliation more organized, traceable, and efficient.*