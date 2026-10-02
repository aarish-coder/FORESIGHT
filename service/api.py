from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from pathlib import Path


# ============================================================
# FORESIGHT SCORING API
# ============================================================

app = FastAPI(
    title="FORESIGHT API",
    description="Demand & Inventory Intelligence Scoring Service",
    version="1.0.0"
)


RISK_FILE = Path(
    "outputs/risk/risk_results.csv"
)


# ------------------------------------------------------------
# Request model
# ------------------------------------------------------------

class ProductRequest(BaseModel):
    product_no: str


# ------------------------------------------------------------
# Health check
# ------------------------------------------------------------

@app.get("/")
def home():

    return {
        "service": "FORESIGHT",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ------------------------------------------------------------
# Product scoring
# ------------------------------------------------------------

@app.post("/score")
def score_product(request: ProductRequest):

    if not RISK_FILE.exists():

        raise HTTPException(
            status_code=500,
            detail="Risk dataset not found."
        )

    df = pd.read_csv(RISK_FILE)

    result = df[
        df["product_no"].astype(str)
        == str(request.product_no)
    ]

    if result.empty:

        raise HTTPException(
            status_code=404,
            detail="Product not found."
        )

    row = result.iloc[0]

    return {
        "product_no": str(row["product_no"]),
        "product_description": str(
            row["product_description"]
        ),
        "quantity_on_hand": float(
            row["qty_on_hand"]
        ),
        "stockout_risk": str(
            row["stockout_risk"]
        ),
        "overstock_risk": str(
            row["overstock_risk"]
        ),
        "risk_score": int(
            row["risk_score"]
        ),
        "decision": str(
            row["decision"]
        ),
        "rupee_value_at_stake": float(
            row["rupee_value_at_stake"]
        )
    }