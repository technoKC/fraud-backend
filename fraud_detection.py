import pandas as pd
import numpy as np
from typing import Dict, List, Any

class FraudDetector:
    def __init__(self):
        # Fraud indicators for VPA patterns
        self.fraud_vpa_patterns = [
            'pay', 'rzp', 'bonus', 'win', 'loan', 'cashback', 
            'credit', 'reward', 'prize', 'offer', 'lucky'
        ]
    
    def detect_fraud(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect fraud transactions based on IS_FRAUD column and patterns"""
        results = {
            "fraud_count": 0,
            "fraud_transactions": [],
            "detailed_results": []
        }
        
        for idx, row in df.iterrows():
            # Check if it's marked as fraud in CSV
            is_fraud = bool(row.get('IS_FRAUD', 0))
            
            # Additional pattern checking
            payer_vpa = str(row.get('PAYER_VPA', '')).lower()
            beneficiary_vpa = str(row.get('BENEFICIARY_VPA', '')).lower()
            
            # Check for suspicious patterns
            suspicious_patterns = []
            for pattern in self.fraud_vpa_patterns:
                if pattern in payer_vpa or pattern in beneficiary_vpa:
                    suspicious_patterns.append(pattern)
            
            # Calculate risk score (0-100)
            risk_score = 0
            if is_fraud:
                risk_score = 80
            if suspicious_patterns:
                risk_score = max(risk_score, 60 + len(suspicious_patterns) * 10)
            
            # Determine risk level
            if risk_score >= 70:
                risk_level = "High"
            elif risk_score >= 40:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            transaction_result = {
                "transaction_id": row.get('TRANSACTION_ID', f'TXN_{idx}'),
                "timestamp": row.get('TXN_TIMESTAMP', ''),
                "amount": float(row.get('AMOUNT', 0)),
                "payer_vpa": row.get('PAYER_VPA', 'Unknown'),
                "beneficiary_vpa": row.get('BENEFICIARY_VPA', 'Unknown'),
                "is_fraud": is_fraud,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "suspicious_patterns": suspicious_patterns,
                "explanation": self._generate_explanation(is_fraud, suspicious_patterns)
            }
            
            results["detailed_results"].append({
                "transaction": transaction_result,
                "classification": {
                    "label": "Fraud" if is_fraud else "Legitimate",
                    "confidence": risk_score / 100,
                    "risk": risk_level
                },
                "explanation": [transaction_result["explanation"]]
            })
            
            if is_fraud:
                results["fraud_count"] += 1
                results["fraud_transactions"].append(transaction_result)
        
        return results
    
    def _generate_explanation(self, is_fraud: bool, patterns: List[str]) -> str:
        """Generate explanation for fraud detection"""
        explanations = []
        
        if is_fraud:
            explanations.append("Transaction flagged as fraudulent in historical data")
        
        if patterns:
            explanations.append(f"Suspicious VPA patterns detected: {', '.join(patterns)}")
        
        if not explanations:
            explanations.append("Transaction appears legitimate")
        
        return "; ".join(explanations)