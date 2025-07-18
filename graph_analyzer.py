import pandas as pd
import networkx as nx
from pyvis.network import Network
import json
from typing import Dict, List, Any

class GraphAnalyzer:
    def create_graph(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create network graph data from transactions"""
        G = nx.DiGraph()
        
        # Add nodes and edges
        for idx, row in df.iterrows():
            payer = str(row.get('PAYER_VPA', f'Unknown_{idx}'))
            beneficiary = str(row.get('BENEFICIARY_VPA', f'Unknown_{idx}'))
            amount = float(row.get('AMOUNT', 0))
            is_fraud = bool(row.get('IS_FRAUD', 0))
            
            # Add nodes
            G.add_node(payer, type='user', fraud=is_fraud)
            G.add_node(beneficiary, type='user', fraud=is_fraud)
            
            # Add edge (transaction)
            G.add_edge(
                payer, 
                beneficiary, 
                amount=amount,
                fraud=is_fraud,
                transaction_id=row.get('TRANSACTION_ID', f'TXN_{idx}')
            )
        
        # Convert to format suitable for visualization
        nodes = []
        edges = []
        
        for node in G.nodes():
            node_data = G.nodes[node]
            nodes.append({
                "id": node,
                "label": node.split('@')[0] if '@' in node else node[:10],
                "color": "#ef4444" if node_data.get('fraud', False) else "#22c55e",
                "size": 25,
                "fraud": node_data.get('fraud', False)
            })
        
        for edge in G.edges():
            edge_data = G.edges[edge]
            edges.append({
                "from": edge[0],
                "to": edge[1],
                "color": "#ef4444" if edge_data.get('fraud', False) else "#3b82f6",
                "width": 2 if edge_data.get('fraud', False) else 1,
                "label": f"₹{edge_data.get('amount', 0):,.0f}",
                "fraud": edge_data.get('fraud', False)
            })
        
        # Calculate statistics
        fraud_nodes = len([n for n in nodes if n['fraud']])
        fraud_edges = len([e for e in edges if e['fraud']])
        
        return {
            "nodes": nodes,
            "edges": edges,
            "statistics": {
                "total_nodes": len(nodes),
                "fraud_nodes": fraud_nodes,
                "total_transactions": len(edges),
                "fraud_transactions": fraud_edges
            }
        }