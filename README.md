# FORESIGHT

## AI-Powered Demand & Inventory Intelligence Platform

FORESIGHT is an inventory intelligence platform designed to help businesses identify inventory risks and prioritize actions.

## Features

- Data cleaning and preparation
- Inventory analysis
- Inventory risk identification
- Stockout risk detection
- Overstock risk detection
- Product-level recommendations
- Interactive Streamlit dashboard
- FastAPI scoring service

## Project Structure

```text
FORESIGHT/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── src/
│   ├── data_cleaning.py
│   ├── analysis.py
│   ├── forecasting.py
│   ├── risk_analysis.py
│   └── recommendations.py
│
├── outputs/
│   ├── forecasts/
│   ├── risk/
│   └── recommendations/
│
├── app/
│   └── dashboard.py
│
├── service/
│   └── api.py
│
├── reports/
│
├── requirements.txt
└── README.md