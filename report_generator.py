from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import pandas as pd
from datetime import datetime
import os
from typing import List, Dict

class ReportGenerator:
    def __init__(self):
        self.reports_dir = "reports"
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
    
    def generate_report(self, df: pd.DataFrame, fraud_transactions: List[Dict], 
                       transaction_statuses: Dict[str, str]) -> str:
        """Generate PDF report for fraud transactions"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fraud_report_{timestamp}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        # Create PDF
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        
        # Header with logo and title
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(colors.HexColor("#0f172a"))
        c.drawString(100, height - 80, "FRAUD DETECTION REPORT")
        
        # Central Bank of India text
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#f59e0b"))
        c.drawString(100, height - 110, "Central Bank of India")
        
        # Report metadata
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.black)
        c.drawString(100, height - 140, f"Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        c.drawString(100, height - 160, f"Total Transactions Analyzed: {len(df):,}")
        c.drawString(100, height - 180, f"Fraud Transactions Detected: {len(fraud_transactions)}")
        
        # Calculate percentages
        fraud_percentage = (len(fraud_transactions) / len(df)) * 100 if len(df) > 0 else 0
        c.drawString(100, height - 200, f"Fraud Rate: {fraud_percentage:.2f}%")
        
        # Status counts
        blocked_count = sum(1 for status in transaction_statuses.values() if status == "blocked")
        verified_count = sum(1 for status in transaction_statuses.values() if status == "verified")
        c.drawString(100, height - 220, f"Blocked Transactions: {blocked_count}")
        c.drawString(100, height - 240, f"Verified Transactions: {verified_count}")
        
        # Fraud transactions table header
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, height - 280, "Fraud Transaction Details")
        
        # Table headers
        y_position = height - 310
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y_position, "Transaction ID")
        c.drawString(170, y_position, "Amount (₹)")
        c.drawString(250, y_position, "Payer VPA")
        c.drawString(380, y_position, "Status")
        
        # Draw line
        c.line(50, y_position - 5, width - 50, y_position - 5)
        
        # Transaction details
        c.setFont("Helvetica", 9)
        y_position -= 20
        
        for i, txn in enumerate(fraud_transactions[:20]):  # Show first 20 transactions
            if y_position < 100:  # Start new page if needed
                c.showPage()
                y_position = height - 100
            
            txn_id = txn['transaction_id']
            status = transaction_statuses.get(txn_id, "Pending")
            
            c.drawString(50, y_position, txn_id[:15] + "...")
            c.drawString(170, y_position, f"{txn['amount']:,.2f}")
            c.drawString(250, y_position, txn['payer_vpa'][:20] + "...")
            
            # Color code status
            if status == "blocked":
                c.setFillColor(colors.red)
            elif status == "verified":
                c.setFillColor(colors.green)
            else:
                c.setFillColor(colors.orange)
            
            c.drawString(380, y_position, status.capitalize())
            c.setFillColor(colors.black)
            
            y_position -= 18
        
        # Footer
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(50, 50, "This is a system-generated report. For queries, contact Central Bank of India Fraud Detection Unit.")
        
        # Save PDF
        c.save()
        
        return filepath