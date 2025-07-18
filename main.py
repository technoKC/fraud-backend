from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import pandas as pd
import json
import os
from fraud_detection import FraudDetector
from graph_analyzer import GraphAnalyzer
from report_generator import ReportGenerator
from typing import List, Dict, Any
from datetime import datetime

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
fraud_detector = FraudDetector()
graph_analyzer = GraphAnalyzer()
report_generator = ReportGenerator()

# Admin credentials (in production, use proper authentication)
ADMIN_USERNAME = "centralbank"
ADMIN_PASSWORD = "admin123"

class AdminLogin(BaseModel):
    username: str
    password: str

class TransactionAction(BaseModel):
    transaction_id: str
    action: str  # "verify" or "block"

# Store for transaction statuses
transaction_statuses = {}

@app.get("/")
async def root():
    return {"message": "FraudShield API is running"}

@app.post("/detect/")
async def detect_fraud(file: UploadFile = File(...)):
    """Upload CSV and detect fraud transactions"""
    try:
        # Save uploaded file
        contents = await file.read()
        df = pd.read_csv(pd.io.common.BytesIO(contents))
        
        # Detect fraud
        fraud_results = fraud_detector.detect_fraud(df)
        
        # Generate graph data
        graph_data = graph_analyzer.create_graph(df)
        
        return {
            "total_transactions": len(df),
            "fraud_detected": fraud_results["fraud_count"],
            "fraud_transactions": fraud_results["fraud_transactions"],
            "graph_data": graph_data,
            "results": fraud_results["detailed_results"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/admin/login/")
async def admin_login(credentials: AdminLogin):
    """Admin login endpoint"""
    if credentials.username == ADMIN_USERNAME and credentials.password == ADMIN_PASSWORD:
        return {"status": "success", "message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/admin/data/")
async def get_admin_data():
    """Load data from backend CSV file"""
    try:
        csv_path = os.path.join("data", "anonymized_sample_fraud_txn.csv")
        df = pd.read_csv(csv_path)
        
        # Detect fraud
        fraud_results = fraud_detector.detect_fraud(df)
        
        # Generate graph data
        graph_data = graph_analyzer.create_graph(df)
        
        # Get transaction statuses
        fraud_transactions = fraud_results["fraud_transactions"]
        for txn in fraud_transactions:
            txn_id = txn["transaction_id"]
            if txn_id in transaction_statuses:
                txn["status"] = transaction_statuses[txn_id]
        
        return {
            "total_transactions": len(df),
            "fraud_detected": fraud_results["fraud_count"],
            "fraud_transactions": fraud_transactions,
            "graph_data": graph_data,
            "blocked_accounts": len([s for s in transaction_statuses.values() if s == "blocked"]),
            "verified_accounts": len([s for s in transaction_statuses.values() if s == "verified"]),
            "system_health": 99.5
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/transaction-action/")
async def update_transaction_status(action: TransactionAction):
    """Update transaction status (verify/block)"""
    transaction_statuses[action.transaction_id] = action.action
    return {"status": "success", "transaction_id": action.transaction_id, "action": action.action}

@app.get("/admin/generate-report/")
async def generate_report():
    """Generate PDF report"""
    try:
        csv_path = os.path.join("data", "anonymized_sample_fraud_txn.csv")
        df = pd.read_csv(csv_path)
        
        # Detect fraud
        fraud_results = fraud_detector.detect_fraud(df)
        
        # Generate report
        report_path = report_generator.generate_report(
            df, 
            fraud_results["fraud_transactions"],
            transaction_statuses
        )
        
        return FileResponse(
            report_path,
            media_type='application/pdf',
            filename=f'fraud_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)