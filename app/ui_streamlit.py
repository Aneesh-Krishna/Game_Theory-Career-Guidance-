# app/ui_streamlit.py

import streamlit as st
import os
from agents.career_agent import handle_user_input
from game_theory.career_game_model import (
    CareerGameModel, update_global_career_matrix, 
    visualize_career_heatmap, explain_game_theory_choice
)
from utils.db_handler import load_session, save_session

def parse_agent_response_for_careers(agent_result: dict) -> dict:
    """
    Parse the enhanced agent result to extract career options and scores
    
    Args:
        agent_result: The enhanced result dictionary from the career agent
        
    Returns:
        Dictionary with career matrix data or None if parsing fails
    """
    try:
        # Check if structured career data is available
        if agent_result.get('career_matrix') and agent_result.get('criteria_labels'):
            return {
                'career_matrix': agent_result['career_matrix'],
                'criteria_labels': agent_result['criteria_labels'],
                'raw_data': agent_result.get('raw_career_data')
            }
        
        # Fallback to text parsing
        response_text = agent_result.get('response', '')
        if response_text:
            # Try to extract career information from text
            from game_theory.career_game_model import parse_agent_response_text
            parsed = parse_agent_response_text(response_text)
            return parsed
        
        return None
        
    except Exception as e:
        st.error(f"Error parsing agent response: {e}")
        return None

def extract_career_matrix_from_context(chat_history: list) -> dict:
    """
    Extract career matrix from the conversation context
    This function analyzes the chat history to build a dynamic career matrix
    
    Args:
        chat_history: List of conversation entries
        
    Returns:
        Dictionary with career matrix or None
    """
    
    # Analyze recent conversations for career mentions
    careers_mentioned = set()
    
    for entry in chat_history[-5:]:  # Look at last 5 entries
        agent_response = entry.get('agent', '')
        user_input = entry.get('user', '')
        
        # Simple keyword extraction (customize as needed)
        career_keywords = [
            'software engineer', 'data scientist', 'product manager',
            'consultant', 'researcher', 'entrepreneur', 'designer',
            'analyst', 'developer', 'manager', 'scientist'
        ]
        
        text_to_analyze = (agent_response + ' ' + user_input).lower()
        
        for keyword in career_keywords:
            if keyword in text_to_analyze:
                careers_mentioned.add(keyword.title())
    
    # If we found career mentions, create a basic matrix
    if careers_mentioned and len(careers_mentioned) >= 2:
        # Create a simplified matrix based on mentioned careers
        # This is a placeholder - you'd want more sophisticated scoring
        career_matrix = {}
        for career in careers_mentioned:
            # Generate basic scores (customize this logic)
            career_matrix[career] = [7, 6, 7, 5, 6]  # Default middle scores
        
        return career_matrix
    
    return None

def main():
    # --- Setup Page ---
    os.makedirs("data", exist_ok=True)

    st.set_page_config(page_title="AI Career Guide", layout="wide")

    st.title("🎯 AI Career Guide - Powered by Game Theory")
    st.markdown("Ask your career questions, and let AI + Game Theory analyze your best options!")

    # --- Initialize Career Game Model ---
    if "career_model" not in st.session_state:
        st.session_state.career_model = CareerGameModel()

    # --- Session State ---
    user_id = "default_user"  # You can replace this with a login/session id
    if "history" not in st.session_state:
        st.session_state.history = load_session(user_id).get("history", [])

    # --- Sidebar Chat History ---
    st.sidebar.title("💬 Chat History")
    
    # Add option to update career matrix manually
    with st.sidebar.expander("🔧 Advanced Settings"):
        st.subheader("Update Career Matrix")
        
        if st.button("🔄 Auto-Update from Conversation"):
            # Try to extract career matrix from conversation
            extracted_matrix = extract_career_matrix_from_context(st.session_state.history)
            if extracted_matrix:
                st.session_state.career_model.update_career_matrix(extracted_matrix)
                st.success(f"Updated matrix with {len(extracted_matrix)} careers!")
            else:
                st.info("No suitable career data found in conversation.")
        
        # Manual matrix update option
        st.subheader("Manual Career Entry")
        career_name = st.text_input("Career Name:", placeholder="e.g., AI Engineer")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            salary = st.slider("Salary", 1, 10, 7, key="salary")
        with col2:
            stability = st.slider("Stability", 1, 10, 6, key="stability")  
        with col3:
            growth = st.slider("Growth", 1, 10, 7, key="growth")
        with col4:
            risk_resistance = st.slider("Risk Resistance", 1, 10, 5, key="risk")
        with col5:
            ease_education = st.slider("Ease of Education", 1, 10, 6, key="education")
        
        if st.button("➕ Add Career") and career_name:
            current_matrix = st.session_state.career_model.career_matrix.copy()
            current_matrix[career_name] = [salary, stability, growth, risk_resistance, ease_education]
            st.session_state.career_model.update_career_matrix(current_matrix)
            st.success(f"Added {career_name} to the career matrix!")

    # Display chat history
    for i, entry in enumerate(st.session_state.history):
        st.sidebar.markdown(f"**You:** {entry['user'][:50]}...")
        st.sidebar.markdown(f"**AI:** {entry['agent'][:50]}...")

    # --- User Input ---
    user_input = st.text_input("📝 Enter your current status or career question:", 
                              placeholder="e.g. Should I pursue Data Science or go for an MBA?")

    if st.button("🔍 Analyze"):
        if user_input:
            with st.spinner("🤖 AI is analyzing your query..."):
                # Get enhanced result from agent (now returns dict instead of string)
                agent_result = handle_user_input(user_input)
            
            # Extract response text for display
            response_text = agent_result.get('response', 'No response received')
            
            # Save to history (save text response for history)
            st.session_state.history.append({"user": user_input, "agent": response_text})
            save_session(user_id, {"history": st.session_state.history})

            # Try to update career matrix from agent result
            if agent_result.get('career_matrix') and agent_result.get('criteria_labels'):
                st.session_state.career_model.update_career_matrix(
                    agent_result['career_matrix'], 
                    agent_result['criteria_labels']
                )
                st.success(f"🔄 Career matrix updated with {len(agent_result['career_matrix'])} careers!")
                
                # Show what careers were added
                with st.expander("🆕 Newly Analyzed Careers"):
                    for career in agent_result['career_matrix'].keys():
                        st.write(f"✅ {career}")
            else:
                # Fallback parsing attempt
                parsed_careers = parse_agent_response_for_careers(agent_result)
                if parsed_careers:
                    st.session_state.career_model.update_career_matrix(
                        parsed_careers['career_matrix'],
                        parsed_careers.get('criteria_labels')
                    )
                    st.info("🔄 Career matrix updated from text analysis!")

            # Display response
            st.subheader("🔎 AI Career Recommendation")
            st.markdown(response_text)

            # Display Game Theory Analysis
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("🧠 Game Theory Analysis")
                explanation = st.session_state.career_model.explain_game_theory_choice()
                st.markdown(explanation)
            
            with col2:
                st.subheader("📈 Career Rankings")
                rankings = st.session_state.career_model.get_career_rankings()
                
                # Sort by worst-case score (minimax strategy)
                sorted_careers = sorted(rankings.items(), 
                                      key=lambda x: x[1]['worst_case_score'], 
                                      reverse=True)
                
                for i, (career, scores) in enumerate(sorted_careers[:5]):
                    medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
                    st.markdown(f"{medal} **{career}**")
                    st.markdown(f"   Worst-case: {scores['worst_case_score']:.1f}")
                    st.markdown(f"   Average: {scores['average_score']:.1f}")

            # Display Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Payoff Matrix Heatmap")
                fig_heatmap = st.session_state.career_model.visualize_career_heatmap()
                st.plotly_chart(fig_heatmap, use_container_width=True)
            
            with col2:
                st.subheader("🌳 Decision Tree")
                fig_tree = st.session_state.career_model.visualize_strategy_tree()
                st.plotly_chart(fig_tree, use_container_width=True)

        else:
            st.warning("Please enter a valid input to analyze.")

    # --- Current Career Matrix Display ---
    with st.expander("👀 View Current Career Matrix"):
        current_matrix = st.session_state.career_model.career_matrix
        criteria = st.session_state.career_model.criteria_labels
        
        st.subheader(f"Current Matrix ({len(current_matrix)} careers)")
        
        # Create a nice table display
        import pandas as pd
        df = pd.DataFrame(current_matrix, index=criteria).T
        st.dataframe(df, use_container_width=True)
        
        # Reset to default option
        if st.button("🔄 Reset to Default Matrix"):
            st.session_state.career_model = CareerGameModel()
            st.success("Reset to default career matrix!")
            st.experimental_rerun()

    # --- Export Options ---
    if st.session_state.history:
        st.subheader("📥 Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export chat history
            chat_text = "\n".join([
                f"User: {entry['user']}\nAI: {entry['agent']}\n---"
                for entry in st.session_state.history
            ])
            st.download_button(
                "💬 Download Chat History",
                data=chat_text,
                file_name="career_chat_history.txt",
                mime="text/plain"
            )
        
        with col2:
            # Export career analysis
            analysis = st.session_state.career_model.explain_game_theory_choice()
            st.download_button(
                "📊 Download Analysis Report",
                data=analysis,
                file_name="career_analysis_report.txt",
                mime="text/plain"
            )

# Allows running independently via `python app/ui_streamlit.py`
if __name__ == "__main__":
    main()