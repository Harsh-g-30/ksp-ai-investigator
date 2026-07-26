# KSP Crime AI Investigator 🔍

**An Intelligent Conversational AI Platform for Crime Database Analysis**

## Live Demo
🔴 **[Live App](https://your-deployed-url-here/app/)**

## What It Does

### ✅ Conversational Crime Intelligence
- **Natural Language Queries**: Ask questions in plain English about crimes, offenders, victims
- **Explainable AI**: Every answer shows the SQL query used and data evidence
- **Smart Query Generation**: GLM-4.7-Flash LLM converts English → SQL automatically

### Example Queries
- "How many murder cases are there?" → **Analyzes crime data, returns count + SQL + evidence**
- "Show repeat offenders" → **Identifies criminals across multiple cases**
- "How many robbery cases?" → **Trends and counts by crime type**

## Key Features

| Feature | Status | Details |
|---------|--------|---------|
| Natural Language Chatbot | ✅ Live | GLM-4.7-Flash powered |
| Explainable AI | ✅ Live | SQL transparency + evidence trails |
| Crime Analytics | ✅ Live | 450 real crime cases in database |
| PDF Export | ✅ Live | Download chat history |
| Repeat Offender Detection | ✅ Live | Identifies criminals across cases |

## Architecture


Frontend: React (Conversational UI)
↓
Backend: Python (Catalyst Advanced I/O)
↓
LLM: GLM-4.7-Flash (Natural Language → SQL)
↓
Database: Catalyst Data Store (26 tables, 450+ cases)


## How It Works

1. **User asks in English**: "How many murder cases?"
2. **LLM generates SQL**: `SELECT COUNT(CaseMasterID) FROM CaseMaster WHERE CrimeMinorHeadID = 1`
3. **Database executes**: Returns result
4. **LLM summarizes**: "There are 15 murder cases in the database"
5. **UI shows**: Answer + SQL query + Raw evidence data

## Tech Stack

- **Frontend**: React 18, CSS3
- **Backend**: Python 3.13, Catalyst Framework
- **LLM**: Zoho QuickML (GLM-4.7-Flash)
- **Database**: Catalyst Data Store (ZCQL)
- **Deployment**: Catalyst AppSail Serverless

## Dataset

- **450 real crime cases** across Karnataka
- **26 relational tables**: Cases, Accused, Victims, Crimes, Arrests, Chargesheets
- **1,131 accused records** with repeat offender identification
- **883 victim records**
- **Crime classifications**: Murder, Robbery, Theft, POCSO, Cyber Crime, etc.

## What Makes This Special

✨ **Transparent AI**: No black boxes — every answer backed by SQL query  
⚡ **Real-time Analysis**: Sub-second queries on 450+ cases  
🎯 **Investigator-Focused**: Designed for law enforcement decision-making  
🔐 **Secure**: Role-based access, audit logs (ready for compliance)  

## Next Phase (Future Enhancements)

- 🌍 Multi-language support (Kannada, Hindi)
- 🎤 Voice interaction
- 📊 Advanced analytics (hotspots, trends, forecasting)
- 🕸️ Criminal network visualization
- 🧠 Behavioral profiling & risk scoring

## Submission Details

**Challenge**: Intelligent Conversational AI for KSP Crime Database  
**Hackathon**: Datathon 2026  
**Team**: Harsh Gaur  
**GitHub**: [Harsh-g-30/ksp-ai-investigator](https://github.com/Harsh-g-30/ksp-ai-investigator)