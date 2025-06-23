# app/game_theory/career_game_model.py

import numpy as np
import plotly.graph_objects as go
import networkx as nx
import plotly.io as pio
from typing import Dict, List, Tuple, Optional
import re

# Default Career Payoff Matrix (fallback)
DEFAULT_CAREER_MATRIX = {
    "Software Engineer": [9, 6, 7, 6, 6],
    "Data Scientist": [8, 7, 8, 5, 6],
    "MBA": [6, 5, 9, 3, 9],
    "UX Designer": [7, 6, 6, 7, 7],
    "Entrepreneur": [9, 3, 10, 2, 4],
    "Researcher (PhD)": [5, 8, 6, 7, 2]
}

DEFAULT_CRITERIA_LABELS = ["Salary", "Stability", "Growth", "Risk-Resistance", "Ease of Education"]

class CareerGameModel:
    """
    Career Game Theory Model that supports dynamic career matrices
    """
    
    def __init__(self, career_matrix: Optional[Dict[str, List[float]]] = None, 
                 criteria_labels: Optional[List[str]] = None):
        """
        Initialize the Career Game Model
        
        Args:
            career_matrix: Dictionary mapping career names to payoff scores
            criteria_labels: List of criteria labels for evaluation
        """
        self.career_matrix = career_matrix or DEFAULT_CAREER_MATRIX
        self.criteria_labels = criteria_labels or DEFAULT_CRITERIA_LABELS
    
    def update_career_matrix(self, career_matrix: Dict[str, List[float]], 
                           criteria_labels: Optional[List[str]] = None):
        """
        Update the career matrix with new data
        
        Args:
            career_matrix: New career matrix data
            criteria_labels: Optional new criteria labels
        """
        self.career_matrix = career_matrix
        if criteria_labels:
            self.criteria_labels = criteria_labels
    
    def get_payoff_matrix(self) -> Tuple[np.ndarray, List[str]]:
        """
        Get the payoff matrix as numpy array and career list
        
        Returns:
            Tuple of (payoff_matrix, career_names)
        """
        return np.array(list(self.career_matrix.values())), list(self.career_matrix.keys())
    
    def calculate_strategy_scores(self) -> Tuple[int, np.ndarray]:
        """
        Calculate minimax strategy scores
        
        Returns:
            Tuple of (best_strategy_index, worst_case_payoffs)
        """
        payoff_matrix, _ = self.get_payoff_matrix()
        worst_case_payoffs = np.min(payoff_matrix, axis=1)
        best_strategy_idx = np.argmax(worst_case_payoffs)
        return best_strategy_idx, worst_case_payoffs
    
    def visualize_career_heatmap(self):
        """
        Create and display a heatmap visualization of the career matrix
        """
        matrix, careers = self.get_payoff_matrix()
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=self.criteria_labels,
            y=careers,
            colorscale='Viridis',
            hoverongaps=False,
            hovertemplate='<b>%{y}</b><br>' +
                         '<b>%{x}</b>: %{z}<br>' +
                         '<extra></extra>'
        ))

        fig.update_layout(
            title="📊 Career Strategy Payoff Matrix",
            xaxis_title="Evaluation Criteria",
            yaxis_title="Career Options",
            height=500,
            font=dict(size=12)
        )
        return fig
    
    def visualize_strategy_tree(self):
        """
        Create a decision tree visualization showing career options and their total scores
        """
        matrix, careers = self.get_payoff_matrix()
        total_scores = matrix.sum(axis=1)

        G = nx.DiGraph()
        G.add_node("Start")

        for i, career in enumerate(careers):
            score = total_scores[i]
            G.add_edge("Start", career, weight=score)

        pos = nx.spring_layout(G, seed=42)

        edge_x = []
        edge_y = []

        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines')

        node_x, node_y, node_text = [], [], []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            if node == "Start":
                label = node
            else:
                total_score = total_scores[careers.index(node)]
                label = f"{node}<br>Total: {total_score:.1f}"
            node_text.append(label)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            marker=dict(
                size=40,
                color=['lightblue' if n != "Start" else 'gold' for n in G.nodes()],
                line_width=2
            ),
            hovertemplate='<b>%{text}</b><extra></extra>'
        )

        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title="🌳 Strategy Tree (Total Payoff)",
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            height=500,
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                        ))
        return fig
    
    def explain_game_theory_choice(self) -> str:
        """
        Generate a detailed explanation of the game theory career choice
        
        Returns:
            Formatted explanation string
        """
        matrix, careers = self.get_payoff_matrix()
        idx, worst_scores = self.calculate_strategy_scores()
        best_career = careers[idx]
        best_score = worst_scores[idx]

        # Create breakdown of worst-case scores
        breakdown = "\n".join([f"• {career}: worst-case score = {score}" 
                              for career, score in zip(careers, worst_scores)])

        explanation = f"""
🧠 **Game Theory Career Decision (Minimax Strategy)**

Using a risk-averse approach with **Minimax** algorithm:
- Each career is evaluated based on its **worst performance** across {len(self.criteria_labels)} criteria
- The career with the **best worst-case payoff** is selected
- This ensures optimal performance even in unfavorable scenarios

🔢 **Worst-case Payoffs Analysis**:
{breakdown}

✅ **Recommended (Minimax Optimal):** **{best_career}** 
   - Worst-case score: **{best_score}**
   - This career provides the best guaranteed minimum performance

📊 **Evaluation Criteria**: {', '.join(self.criteria_labels)}

💡 **Strategy Rationale**: This approach minimizes regret by choosing the option that performs best in the worst-case scenario, making it ideal for risk-averse decision making.
"""
        return explanation
    
    def get_career_rankings(self) -> Dict[str, Dict[str, float]]:
        """
        Get comprehensive career rankings based on different strategies
        
        Returns:
            Dictionary with career rankings and scores
        """
        matrix, careers = self.get_payoff_matrix()
        
        # Calculate different scoring methods
        total_scores = matrix.sum(axis=1)
        avg_scores = matrix.mean(axis=1)
        worst_scores = matrix.min(axis=1)
        best_scores = matrix.max(axis=1)
        
        rankings = {}
        for i, career in enumerate(careers):
            rankings[career] = {
                'total_score': float(total_scores[i]),
                'average_score': float(avg_scores[i]),
                'worst_case_score': float(worst_scores[i]),
                'best_case_score': float(best_scores[i]),
                'payoff_vector': matrix[i].tolist()
            }
        
        return rankings


# Global instance for backward compatibility
_global_model = CareerGameModel()

# Legacy functions for backward compatibility
def get_payoff_matrix():
    """Legacy function - use CareerGameModel.get_payoff_matrix() instead"""
    return _global_model.get_payoff_matrix()

def calculate_strategy_scores(payoff_matrix):
    """Legacy function - use CareerGameModel.calculate_strategy_scores() instead"""
    return _global_model.calculate_strategy_scores()

def visualize_career_heatmap():
    """Legacy function - use CareerGameModel.visualize_career_heatmap() instead"""
    fig = _global_model.visualize_career_heatmap()
    fig.show()

def visualize_strategy_tree():
    """Legacy function - use CareerGameModel.visualize_strategy_tree() instead"""
    fig = _global_model.visualize_strategy_tree()
    fig.show()

def explain_game_theory_choice():
    """Legacy function - use CareerGameModel.explain_game_theory_choice() instead"""
    return _global_model.explain_game_theory_choice()

def update_global_career_matrix(career_matrix: Dict[str, List[float]], 
                               criteria_labels: Optional[List[str]] = None):
    """
    Update the global career matrix
    
    Args:
        career_matrix: New career matrix data
        criteria_labels: Optional new criteria labels
    """
    global _global_model
    _global_model.update_career_matrix(career_matrix, criteria_labels)

# Function to create model instance with agent data
def create_model_from_agent_data(agent_result: Dict) -> CareerGameModel:
    """
    Create a CareerGameModel instance from agent response data
    
    Args:
        agent_result: Dictionary result from enhanced career agent
        
    Returns:
        CareerGameModel instance with parsed data
    """
    try:
        if agent_result.get('career_matrix') and agent_result.get('criteria_labels'):
            return CareerGameModel(
                career_matrix=agent_result['career_matrix'],
                criteria_labels=agent_result['criteria_labels']
            )
        else:
            # Fallback to parsing response text
            parsed_data = parse_agent_response_text(agent_result.get('response', ''))
            if parsed_data:
                return CareerGameModel(
                    career_matrix=parsed_data['career_matrix'],
                    criteria_labels=parsed_data['criteria_labels']
                )
            else:
                return CareerGameModel()  # Return default model
                
    except Exception as e:
        print(f"Error creating model from agent data: {e}")
        return CareerGameModel()  # Return default model

def parse_agent_response_text(response_text: str) -> Optional[Dict]:
    """
    Parse agent response text to extract career information
    
    Args:
        response_text: Raw text response from agent
        
    Returns:
        Dictionary with career_matrix and criteria_labels or None
    """
    import re
    import json
    
    try:
        # Look for CAREER_MATRIX section
        matrix_match = re.search(r'CAREER_MATRIX:\s*```json\s*(.*?)\s*```', response_text, re.DOTALL | re.IGNORECASE)
        
        if matrix_match:
            json_str = matrix_match.group(1)
            career_data = json.loads(json_str)
            
            if 'careers' in career_data:
                # Convert to game theory format
                careers = career_data['careers']
                criteria_order = [
                    'salary_potential', 'job_security', 'growth_opportunity', 
                    'work_life_balance', 'skill_transferability', 'market_demand',
                    'education_barrier', 'remote_flexibility'
                ]
                
                career_matrix = {}
                for career_name, scores in careers.items():
                    score_vector = []
                    for criterion in criteria_order:
                        score_vector.append(scores.get(criterion, 5))
                    career_matrix[career_name] = score_vector
                
                criteria_labels = [c.replace('_', ' ').title() for c in criteria_order]
                
                return {
                    'career_matrix': career_matrix,
                    'criteria_labels': criteria_labels
                }
        
        # Fallback: look for career mentions in text
        career_mentions = extract_careers_from_text(response_text)
        if career_mentions:
            return create_basic_matrix_from_mentions(career_mentions)
            
        return None
        
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error parsing agent response: {e}")
        return None

def extract_careers_from_text(text: str) -> List[str]:
    """
    Extract career names from free text
    
    Args:
        text: Text to analyze
        
    Returns:
        List of identified career names
    """
    # Common career patterns
    career_patterns = [
        r'\b(software engineer|data scientist|product manager|consultant|researcher|analyst)\b',
        r'\b(developer|designer|manager|scientist|engineer|architect|specialist)\b',
        r'\b(MBA|PhD|master\'s|bachelor\'s)\b.*?\b(holder|graduate|student)\b',
        r'\b(marketing|sales|finance|operations|strategy|consulting)\b.*?(?:role|position|career|job)',
    ]
    
    careers_found = set()
    text_lower = text.lower()
    
    for pattern in career_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                careers_found.update(match)
            else:
                careers_found.add(match)
    
    # Clean and format career names
    formatted_careers = []
    for career in careers_found:
        if len(career) > 2:  # Filter out very short matches
            formatted_career = career.replace('_', ' ').title()
            if formatted_career not in formatted_careers:
                formatted_careers.append(formatted_career)
    
    return formatted_careers[:6]  # Limit to 6 careers

def create_basic_matrix_from_mentions(career_mentions: List[str]) -> Dict:
    """
    Create a basic career matrix from mentioned careers
    
    Args:
        career_mentions: List of career names
        
    Returns:
        Dictionary with basic career matrix
    """
    # Basic scoring based on general career knowledge
    career_defaults = {
        'software engineer': [9, 8, 8, 7, 8, 9, 6, 9],
        'data scientist': [8, 7, 9, 6, 8, 8, 5, 8],
        'product manager': [8, 7, 8, 6, 9, 8, 7, 7],
        'consultant': [7, 6, 7, 4, 9, 6, 6, 6],
        'researcher': [6, 8, 6, 8, 7, 5, 4, 7],
        'analyst': [6, 7, 6, 7, 7, 7, 7, 6],
        'designer': [6, 6, 7, 7, 7, 7, 6, 8],
        'manager': [7, 7, 8, 5, 8, 7, 8, 6],
        'developer': [8, 7, 7, 7, 7, 8, 6, 8],
        'architect': [9, 8, 7, 6, 8, 7, 5, 7],
    }
    
    career_matrix = {}
    for career in career_mentions:
        career_key = career.lower()
        # Find best match in defaults
        best_match = None
        for default_key in career_defaults:
            if default_key in career_key or career_key in default_key:
                best_match = default_key
                break
        
        if best_match:
            career_matrix[career] = career_defaults[best_match]
        else:
            # Generic scoring for unknown careers
            career_matrix[career] = [6, 6, 6, 6, 6, 6, 6, 6]
    
    criteria_labels = [
        'Salary Potential', 'Job Security', 'Growth Opportunity', 
        'Work Life Balance', 'Skill Transferability', 'Market Demand',
        'Education Barrier', 'Remote Flexibility'
    ]
    
    return {
        'career_matrix': career_matrix,
        'criteria_labels': criteria_labels
    }

# Run for testing
if __name__ == "__main__":
    # Test with default data
    model = CareerGameModel()
    
    print("=== Testing Career Game Model ===")
    print(model.explain_game_theory_choice())
    
    # Test updating matrix
    new_matrix = {
        "AI Engineer": [10, 7, 9, 5, 7],
        "Product Manager": [8, 8, 8, 6, 8],
        "Consultant": [7, 6, 7, 4, 9]
    }
    
    model.update_career_matrix(new_matrix)
    print("\n=== After updating matrix ===")
    print(model.explain_game_theory_choice())
    
    # Show visualizations
    fig1 = model.visualize_career_heatmap()
    fig2 = model.visualize_strategy_tree()
    # Uncomment to show plots:
    # fig1.show()
    # fig2.show()