# AI Agents

This repository provides scripts for working with AI agents, including weather data retrieval.

## Script Overview

The `04b-azure-ai-agent-private-openapi-auth-header.py` script demonstrates how to use Azure AI Agents with private OpenAPI plugins that require authentication headers. It loads OpenAPI specifications for weather and electricity data, sets up authentication using a bearer token, and queries the agent for information using these plugins.

## Setup Instructions

Follow these steps to set up your environment and run the script:

### 1. Create a Virtual Environment

```bash
python -m venv venv
```

### 2. Activate the Virtual Environment

- On Linux/macOS:
```bash
source venv/bin/activate
```
- On Windows:
```cmd
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Python Script

Run the main script in this repository:

```bash
python 04b-azure-ai-agent-private-openapi-auth-header.py
```

---
