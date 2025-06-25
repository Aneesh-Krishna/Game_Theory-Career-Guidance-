# app/ui_streamlit.py

import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import base64
from datetime import datetime
from agents.career_agent import handle_user_input
from game_theory.career_game_model import (
    CareerGameModel, update_global_career_matrix, 
    visualize_career_heatmap, explain_game_theory_choice
)
from utils.db_handler import load_session, save_session

# PDF Export functionality
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

def inject_professional_css():
    """Inject professional CSS styling"""
    st.markdown("""
    <style>
    /* Main page styling */
    .main {
        padding-top: 2rem;
    }
    
    /* Custom header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9ff 0%, #e6f3ff 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Text input styling */
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #e0e6ed;
        transition: border-color 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    
    /* Career ranking cards */
    .career-rank-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .career-rank-1 {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        color: #8b4513;
    }
    
    .career-rank-2 {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #2c5aa0;
    }
    
    .career-rank-3 {
        background: linear-gradient(135deg, #fad0c4 0%, #ffd1ff 100%);
        color: #8b4513;
    }
    
    /* Stats container */
    .stats-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    /* Analysis section */
    .analysis-section {
        background: #f8f9ff;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #e0e6ed;
        margin: 1rem 0;
    }
    
    /* Success/info/warning messages */
    .stSuccess {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        border: none;
        border-radius: 8px;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border: none;
        border-radius: 8px;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        margin-top: 3rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

def create_professional_header():
    """Create a professional header section"""
    st.markdown("""
    <div class="main-header">
        <h1>🎯 AI Career Guide</h1>
        <p>Intelligent Career Guidance Powered by Game Theory & Advanced AI</p>
    </div>
    """, unsafe_allow_html=True)

def create_stats_dashboard(career_model, history):
    """Create a professional stats dashboard"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">📝 Questions Asked</h3>
            <h2 style="margin: 0.5rem 0;">{}</h2>
        </div>
        """.format(len(history)), unsafe_allow_html=True)
    
    with col2:
        career_count = len(career_model.career_matrix) if career_model.career_matrix else 0
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">🏢 Careers Analyzed</h3>
            <h2 style="margin: 0.5rem 0;">{}</h2>
        </div>
        """.format(career_count), unsafe_allow_html=True)
    
    with col3:
        rankings = career_model.get_career_rankings()
        top_score = max([scores['worst_case_score'] for scores in rankings.values()]) if rankings else 0
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">⭐ Top Score</h3>
            <h2 style="margin: 0.5rem 0;">{:.1f}</h2>
        </div>
        """.format(top_score), unsafe_allow_html=True)
    
    with col4:
        session_time = datetime.now().strftime("%I:%M %p")
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">🕒 Session Time</h3>
            <h2 style="margin: 0.5rem 0;">{}</h2>
        </div>
        """.format(session_time), unsafe_allow_html=True)

def create_professional_sidebar():
    """Create a professional sidebar with enhanced features"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; border-radius: 10px; margin-bottom: 1rem;">
            <h2 style="margin: 0;">🚀 Control Panel</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.markdown("### 📍 Navigation")
        page = st.selectbox("Choose Section:", 
                           ["🏠 Main Analysis", "📊 Career Matrix", "📈 Visualizations", "⚙️ Settings"],
                           key="nav_select")
        
        st.divider()
        
        # Quick Stats
        st.markdown("### 📊 Quick Stats")
        if st.session_state.get('history'):
            st.metric("Total Conversations", len(st.session_state.history))
        
        if st.session_state.get('career_model') and st.session_state.career_model.career_matrix:
            st.metric("Careers in Matrix", len(st.session_state.career_model.career_matrix))
        
        st.divider()
        
        # Recent Activity
        st.markdown("### 🕒 Recent Activity")
        if st.session_state.get('history'):
            for i, entry in enumerate(st.session_state.history[-3:]):
                with st.expander(f"💭 Q{len(st.session_state.history)-2+i}", expanded=False):
                    st.write(f"**Question:** {entry['user'][:100]}...")
                    st.write(f"**Response:** {entry['agent'][:150]}...")
        else:
            st.info("No recent activity")
        
        st.divider()
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh", key="refresh_btn"):
                st.rerun()
        with col2:
            if st.button("🗑️ Clear", key="clear_btn"):
                if st.session_state.get('history'):
                    st.session_state.history = []
                    st.success("Cleared!")
                    st.rerun()

def create_enhanced_input_section():
    """Create an enhanced input section with better UX"""
    st.markdown("""
    <div class="analysis-section">
        <h2 style="color: #667eea; margin-bottom: 1rem;">💡 Ask Your Career Question</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample questions for inspiration
    with st.expander("💭 Need Inspiration? Try These Sample Questions"):
        sample_questions = [
            "Should I pursue Data Science or Software Engineering? I have a background in mathematics.",
            "I'm considering an MBA vs staying in my current tech role. What are the pros and cons?",
            "Which career path offers better long-term stability: Product Management or UX Design?",
            "I want to transition from finance to tech. What roles should I consider?",
            "Should I become a consultant or join a startup as an early employee?"
        ]
        
        for i, question in enumerate(sample_questions, 1):
            if st.button(f"📝 {question}", key=f"sample_{i}"):
                st.session_state.sample_question = question
                st.rerun()
    
    # Main input area
    default_text = st.session_state.get('sample_question', '')
    user_input = st.text_area(
        "Enter your career question or current situation:",
        value=default_text,
        placeholder="Describe your background, goals, and the career decisions you're considering...",
        height=120,
        help="Be specific about your background, interests, and the career options you're weighing."
    )
    
    # Clear sample question after use
    if 'sample_question' in st.session_state:
        del st.session_state.sample_question
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        analyze_btn = st.button("🔍 Analyze Career Options", type="primary", key="main_analyze")
    with col2:
        if st.button("💡 Get Suggestions", key="suggestions"):
            st.info("💭 Try asking about specific career comparisons, industry transitions, or skill development paths!")
    with col3:
        if st.session_state.get('history'):
            export_btn = st.button("📥 Export Results", key="quick_export")
    
    return user_input, analyze_btn

def create_professional_career_rankings(rankings):
    """Create professional career ranking display"""
    if not rankings:
        return
    
    st.markdown("""
    <div class="analysis-section">
        <h2 style="color: #667eea; margin-bottom: 1rem;">🏆 Career Rankings</h2>
    </div>
    """, unsafe_allow_html=True)
    
    sorted_careers = sorted(rankings.items(), 
                          key=lambda x: x[1]['worst_case_score'], 
                          reverse=True)
    
    # Top 3 with special styling
    for i, (career, scores) in enumerate(sorted_careers[:3]):
        rank_class = f"career-rank-{i+1}"
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
        
        st.markdown(f"""
        <div class="{rank_class}" style="margin: 1rem 0; padding: 1.5rem; border-radius: 12px;">
            <h3 style="margin: 0; font-size: 1.4rem;">{medal} {career}</h3>
            <div style="display: flex; justify-content: space-around; margin-top: 1rem;">
                <div><strong>Worst-Case:</strong> {scores['worst_case_score']:.1f}</div>
                <div><strong>Average:</strong> {scores['average_score']:.1f}</div>
                <div><strong>Best-Case:</strong> {scores['best_case_score']:.1f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Remaining careers in a compact table
    if len(sorted_careers) > 3:
        st.markdown("#### Other Career Options")
        remaining_data = []
        for i, (career, scores) in enumerate(sorted_careers[3:], 4):
            remaining_data.append({
                'Rank': i,
                'Career': career,
                'Worst-Case': f"{scores['worst_case_score']:.1f}",
                'Average': f"{scores['average_score']:.1f}",
                'Best-Case': f"{scores['best_case_score']:.1f}"
            })
        
        if remaining_data:
            df = pd.DataFrame(remaining_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

def create_enhanced_visualizations(career_model):
    """Create enhanced visualization section"""
    st.markdown("""
    <div class="analysis-section">
        <h2 style="color: #667eea; margin-bottom: 1rem;">📊 Visual Analysis Dashboard</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if not career_model.career_matrix:
        st.info("🎯 Analyze some career options first to see visualizations!")
        return
    
    # Visualization tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔥 Heatmap", "🌳 Decision Tree", "📊 Comparison", "📈 Trends"])
    
    with tab1:
        st.markdown("**Career Criteria Heatmap**")
        fig_heatmap = career_model.visualize_career_heatmap()
        if fig_heatmap:
            fig_heatmap.update_layout(
                height=500,
                template='plotly_white',
                title_font_size=16,
                title_x=0.5
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("Heatmap will appear after career analysis")
    
    with tab2:
        st.markdown("**Strategic Decision Tree**")
        fig_tree = career_model.visualize_strategy_tree()
        if fig_tree:
            fig_tree.update_layout(height=500, template='plotly_white')
            st.plotly_chart(fig_tree, use_container_width=True)
        else:
            st.info("Decision tree will appear after career analysis")
    
    with tab3:
        st.markdown("**Career Score Comparison**")
        if career_model.career_matrix:
            careers = list(career_model.career_matrix.keys())
            total_scores = [sum(scores) for scores in career_model.career_matrix.values()]
            
            fig = px.bar(
                x=careers, 
                y=total_scores,
                title="Total Career Scores",
                color=total_scores,
                color_continuous_scale="Viridis"
            )
            fig.update_layout(
                height=500,
                template='plotly_white',
                xaxis_title="Career Options",
                yaxis_title="Total Score"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown("**Career Criteria Breakdown**")
        if career_model.career_matrix and career_model.criteria_labels:
            # Create radar chart for top 3 careers
            rankings = career_model.get_career_rankings()
            if rankings:
                sorted_careers = sorted(rankings.items(), 
                                      key=lambda x: x[1]['worst_case_score'], 
                                      reverse=True)[:3]
                
                fig = go.Figure()
                
                for career, _ in sorted_careers:
                    if career in career_model.career_matrix:
                        scores = career_model.career_matrix[career]
                        fig.add_trace(go.Scatterpolar(
                            r=scores,
                            theta=career_model.criteria_labels,
                            fill='toself',
                            name=career
                        ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 10]
                        )),
                    height=500,
                    title="Top 3 Careers - Criteria Comparison"
                )
                st.plotly_chart(fig, use_container_width=True)

def create_advanced_settings_panel():
    """Create advanced settings panel"""
    st.markdown("""
    <div class="analysis-section">
        <h2 style="color: #667eea; margin-bottom: 1rem;">⚙️ Advanced Settings</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Career Matrix Management")
        
        if st.button("🔄 Auto-Update from Conversation", key="auto_update"):
            extracted_matrix = extract_career_matrix_from_context(st.session_state.history)
            if extracted_matrix:
                st.session_state.career_model.update_career_matrix(extracted_matrix)
                st.success(f"✅ Updated matrix with {len(extracted_matrix)} careers!")
            else:
                st.info("ℹ️ No suitable career data found in conversation.")
        
        if st.button("🔄 Reset to Default Matrix", key="reset_matrix"):
            st.session_state.career_model = CareerGameModel()
            st.success("✅ Reset to default career matrix!")
            st.rerun()
    
    with col2:
        st.markdown("#### 📊 Export Options")
        
        if st.session_state.get('history'):
            # Quick export buttons
            chat_text = "\n".join([
                f"User: {entry['user']}\nAI: {entry['agent']}\n---"
                for entry in st.session_state.history
            ])
            
            st.download_button(
                "💬 Download Chat History",
                data=chat_text,
                file_name=f"career_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                key="download_chat"
            )
            
            if st.session_state.career_model.career_matrix:
                analysis = st.session_state.career_model.explain_game_theory_choice()
                st.download_button(
                    "📊 Download Analysis",
                    data=analysis,
                    file_name=f"career_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain",
                    key="download_analysis"
                )

def create_manual_career_entry():
    """Create manual career entry section"""
    with st.expander("➕ Add Custom Career"):
        st.markdown("**Manual Career Entry**")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            career_name = st.text_input("Career Name:", placeholder="e.g., AI Engineer", key="manual_career")
        
        with col2:
            st.markdown("**Rate each criterion (1-10):**")
            cols = st.columns(5)
            
            with cols[0]:
                salary = st.slider("💰 Salary", 1, 10, 7, key="manual_salary")
            with cols[1]:
                stability = st.slider("🛡️ Stability", 1, 10, 6, key="manual_stability")  
            with cols[2]:
                growth = st.slider("📈 Growth", 1, 10, 7, key="manual_growth")
            with cols[3]:
                risk_resistance = st.slider("⚖️ Risk Resistance", 1, 10, 5, key="manual_risk")
            with cols[4]:
                ease_education = st.slider("🎓 Education Ease", 1, 10, 6, key="manual_education")
        
        if st.button("✅ Add Career to Matrix", key="add_manual_career") and career_name:
            current_matrix = st.session_state.career_model.career_matrix.copy()
            current_matrix[career_name] = [salary, stability, growth, risk_resistance, ease_education]
            st.session_state.career_model.update_career_matrix(current_matrix)
            st.success(f"✅ Added {career_name} to the career matrix!")
            st.rerun()

# Existing utility functions (keeping the same implementations)
def generate_pdf_report(career_model, chat_history, user_input=""):
    """Generate a comprehensive PDF report of the career analysis"""
    if not PDF_AVAILABLE:
        raise ImportError("ReportLab not installed. Install with: pip install reportlab")
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    # Title Page
    title = Paragraph("🎯 AI Career Guide Analysis Report", title_style)
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Report metadata
    report_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    metadata = f"<b>Generated:</b> {report_date}<br/><b>Query:</b> {user_input}"
    story.append(Paragraph(metadata, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Executive Summary
    story.append(Paragraph("📋 Executive Summary", heading_style))
    
    rankings = career_model.get_career_rankings()
    if rankings:
        sorted_careers = sorted(rankings.items(), 
                              key=lambda x: x[1]['worst_case_score'], 
                              reverse=True)
        
        top_career = sorted_careers[0]
        summary_text = f"""
        Based on game theory analysis of {len(rankings)} career options, 
        <b>{top_career[0]}</b> emerges as the optimal choice with a worst-case score of 
        {top_career[1]['worst_case_score']:.1f} and average score of {top_career[1]['average_score']:.1f}.
        
        This analysis considers multiple criteria including salary potential, job stability, 
        growth opportunities, risk resistance, and ease of education/entry.
        """
        story.append(Paragraph(summary_text, styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # Career Rankings Table
    story.append(Paragraph("🏆 Career Rankings", heading_style))
    
    if rankings:
        # Create table data
        table_data = [['Rank', 'Career', 'Worst-Case Score', 'Average Score', 'Best-Case Score']]
        
        for i, (career, scores) in enumerate(sorted_careers):
            rank = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else str(i+1)
            table_data.append([
                rank,
                career,
                f"{scores['worst_case_score']:.1f}",
                f"{scores['average_score']:.1f}",
                f"{scores['best_case_score']:.1f}"
            ])
        
        # Create and style table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
    
    story.append(Spacer(1, 20))
    
    # Game Theory Analysis
    story.append(Paragraph("🧠 Game Theory Analysis", heading_style))
    explanation = career_model.explain_game_theory_choice()
    story.append(Paragraph(explanation, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Career Matrix Details
    story.append(Paragraph("📊 Detailed Career Matrix", heading_style))
    
    matrix = career_model.career_matrix
    criteria = career_model.criteria_labels
    
    if matrix:
        # Create detailed matrix table
        matrix_data = [['Career'] + criteria]
        for career, scores in matrix.items():
            matrix_data.append([career] + [str(score) for score in scores])
        
        matrix_table = Table(matrix_data)
        matrix_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(matrix_table)
    
    story.append(PageBreak())
    
    # Chat History
    story.append(Paragraph("💬 Conversation History", heading_style))
    
    for i, entry in enumerate(chat_history[-10:]):  # Last 10 entries
        story.append(Paragraph(f"<b>Q{i+1}:</b> {entry['user']}", styles['Normal']))
        story.append(Paragraph(f"<b>A{i+1}:</b> {entry['agent'][:500]}{'...' if len(entry['agent']) > 500 else ''}", styles['Normal']))
        story.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_career_comparison_table(career_model):
    """Create a comprehensive career comparison table"""
    rankings = career_model.get_career_rankings()
    matrix = career_model.career_matrix
    criteria = career_model.criteria_labels
    
    if not rankings or not matrix:
        return None
    
    # Create comprehensive comparison data
    comparison_data = []
    
    for career, scores in rankings.items():
        row = {
            'Career': career,
            'Worst-Case Score': scores['worst_case_score'],
            'Average Score': scores['average_score'],
            'Best-Case Score': scores['best_case_score'],
            'Total Score': sum(matrix[career]) if career in matrix else 0
        }
        
        # Add individual criteria scores
        if career in matrix:
            for i, criterion in enumerate(criteria):
                row[criterion] = matrix[career][i]
        
        comparison_data.append(row)
    
    df = pd.DataFrame(comparison_data)
    df = df.sort_values('Worst-Case Score', ascending=False)
    return df

def parse_agent_response_for_careers(agent_result: dict) -> dict:
    """Parse the enhanced agent result to extract career options and scores"""
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
    """Extract career matrix from the conversation context"""
    # Analyze recent conversations for career mentions
    careers_mentioned = set()
    
    for entry in chat_history[-5:]:  # Look at last 5 entries
        agent_response = entry.get('agent', '')
        user_input = entry.get('user', '')
        
        # Simple keyword extraction (customize as needed)
        career_keywords = [
            'software engineer', 'data scientist', 'product manager',
            'consultant', 'researcher', 'entrepreneur', 'designer',
            'analyst', 'developer', 'manager', 'scientist', 'teacher',
            'doctor', 'lawyer', 'architect', 'marketing', 'finance'
        ]
        
        text_to_analyze = (agent_response + ' ' + user_input).lower()
        
        for keyword in career_keywords:
            if keyword in text_to_analyze:
                careers_mentioned.add(keyword.title())
    
    # If we found career mentions, create a basic matrix
    if careers_mentioned and len(careers_mentioned) >= 2:
        # Create a simplified matrix based on mentioned careers
        career_matrix = {}
        for career in careers_mentioned:
            # Generate basic scores (customize this logic)
            career_matrix[career] = [7, 6, 7, 5, 6]  # Default middle scores
        
        return career_matrix
    
    return None

def main():
    """Main application function with professional UI"""
    # --- Setup Page ---
    os.makedirs("data", exist_ok=True)

    st.set_page_config(
        page_title="AI Career Guide Pro", 
        layout="wide",
        page_icon="🎯",
        initial_sidebar_state="expanded"
    )

    # Inject professional styling
    inject_professional_css()
    
    # Create professional header
    create_professional_header()

    # --- Initialize Career Game Model ---
    if "career_model" not in st.session_state:
        st.session_state.career_model = CareerGameModel()
    
    if "current_user_input" not in st.session_state:
        st.session_state.current_user_input = ""

    # --- Session State ---
    user_id = "default_user"  # You can replace this with a login/session id
    if "history" not in st.session_state:
        st.session_state.history = load_session(user_id).get("history", [])

    # --- Professional Sidebar ---
    create_professional_sidebar()
    
    # --- Stats Dashboard ---
    create_stats_dashboard(st.session_state.career_model, st.session_state.history)
    
    st.divider()

    # --- Main Content Based on Navigation ---
    page = st.session_state.get('nav_select', '🏠 Main Analysis')
    
    if page == "🏠 Main Analysis":
        # --- Enhanced Input Section ---
        user_input, analyze_btn = create_enhanced_input_section()
        
        # --- Analysis Processing ---
        if analyze_btn and user_input:
            st.session_state.current_user_input = user_input
            
            with st.spinner("🧠 AI is analyzing your career options..."):
                # Get enhanced result from agent
                agent_result = handle_user_input(user_input)
            
            # Extract response text for display
            response_text = agent_result.get('response', 'No response received')
            
            # Save to history
            st.session_state.history.append({"user": user_input, "agent": response_text})
            save_session(user_id, {"history": st.session_state.history})

            # Try to update career matrix from agent result
            if agent_result.get('career_matrix') and agent_result.get('criteria_labels'):
                st.session_state.career_model.update_career_matrix(
                    agent_result['career_matrix'], 
                    agent_result['criteria_labels']
                )
                st.success(f"🎯 Career matrix updated with {len(agent_result['career_matrix'])} careers!")
                
                # Show what careers were added
                with st.expander("✨ Newly Analyzed Careers"):
                    cols = st.columns(3)
                    for i, career in enumerate(agent_result['career_matrix'].keys()):
                        with cols[i % 3]:
                            st.markdown(f"✅ **{career}**")
            else:
                # Fallback parsing attempt
                parsed_careers = parse_agent_response_for_careers(agent_result)
                if parsed_careers:
                    st.session_state.career_model.update_career_matrix(
                        parsed_careers['career_matrix'],
                        parsed_careers.get('criteria_labels')
                    )
                    st.info("🔄 Career matrix updated from text analysis!")

            # Display response prominently
            st.markdown("""
            <div class="analysis-section">
                <h2 style="color: #667eea; margin-bottom: 1rem;">🤖 AI Career Recommendation</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(response_text)
            
            # Store the latest response for continued display
            st.session_state.latest_response = response_text
            
            st.rerun()  # Refresh to show updated analysis

        # --- Display Latest AI Response (if available) ---
        if hasattr(st.session_state, 'latest_response') and st.session_state.latest_response:
            if not (analyze_btn and user_input):  # Only show if not just analyzed
                st.markdown("""
                <div class="analysis-section">
                    <h2 style="color: #667eea; margin-bottom: 1rem;">🤖 Latest AI Career Recommendation</h2>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(st.session_state.latest_response)

        # --- Display Analysis Results ---
        if st.session_state.career_model.career_matrix:
            st.divider()
            
            # Main Analysis Section with Columns
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.markdown("""
                <div class="analysis-section">
                    <h2 style="color: #667eea; margin-bottom: 1rem;">🧠 Game Theory Analysis</h2>
                </div>
                """, unsafe_allow_html=True)
                explanation = st.session_state.career_model.explain_game_theory_choice()
                st.markdown(explanation)
            
            with col2:
                # Professional Career Rankings
                rankings = st.session_state.career_model.get_career_rankings()
                if rankings:
                    create_professional_career_rankings(rankings)

            st.divider()
            
            # --- Comprehensive Career Comparison Table ---
            st.markdown("""
            <div class="analysis-section">
                <h2 style="color: #667eea; margin-bottom: 1rem;">📊 Comprehensive Career Comparison</h2>
            </div>
            """, unsafe_allow_html=True)
            
            comparison_df = create_career_comparison_table(st.session_state.career_model)
            
            if comparison_df is not None:
                # Display with formatting and interactivity
                st.dataframe(
                    comparison_df.style.format({
                        'Worst-Case Score': '{:.1f}',
                        'Average Score': '{:.1f}',
                        'Best-Case Score': '{:.1f}',
                        'Total Score': '{:.0f}'
                    }).highlight_max(axis=0, subset=['Worst-Case Score', 'Average Score', 'Best-Case Score']),
                    use_container_width=True,
                    height=400
                )

    elif page == "📊 Career Matrix":
        st.markdown("""
        <div class="analysis-section">
            <h2 style="color: #667eea; margin-bottom: 1rem;">📊 Career Matrix Management</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Current Matrix Display
        current_matrix = st.session_state.career_model.career_matrix
        criteria = st.session_state.career_model.criteria_labels
        
        if current_matrix:
            st.markdown(f"### Current Matrix ({len(current_matrix)} careers)")
            
            # Create enhanced matrix display
            df = pd.DataFrame(current_matrix, index=criteria).T
            st.dataframe(
                df.style.highlight_max(axis=0).format('{:.0f}'),
                use_container_width=True,
                height=400
            )
            
            # Matrix statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_scores = df.mean(axis=1)
                st.metric("Highest Average", f"{avg_scores.max():.1f}", f"{avg_scores.idxmax()}")
            with col2:
                total_scores = df.sum(axis=1)
                st.metric("Highest Total", f"{total_scores.max():.0f}", f"{total_scores.idxmax()}")
            with col3:
                st.metric("Total Careers", len(current_matrix))
        else:
            st.info("🎯 No career data available. Ask a career question to get started!")
        
        st.divider()
        
        # Manual Career Entry
        create_manual_career_entry()
        
    elif page == "📈 Visualizations":
        create_enhanced_visualizations(st.session_state.career_model)
        
    elif page == "⚙️ Settings":
        create_advanced_settings_panel()

    # --- Enhanced Export Section (always visible at bottom) ---
    if st.session_state.history:
        st.divider()
        st.markdown("""
        <div class="analysis-section">
            <h2 style="color: #667eea; margin-bottom: 1rem;">📥 Export & Download</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Export chat history
            chat_text = "\n".join([
                f"User: {entry['user']}\nAI: {entry['agent']}\n{'='*50}"
                for entry in st.session_state.history
            ])
            st.download_button(
                "💬 Chat History",
                data=chat_text,
                file_name=f"career_chat_history_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                key="export_chat"
            )
        
        with col2:
            # Export career analysis
            if st.session_state.career_model.career_matrix:
                analysis = st.session_state.career_model.explain_game_theory_choice()
                st.download_button(
                    "📊 Analysis Report",
                    data=analysis,
                    file_name=f"career_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain",
                    key="export_analysis"
                )
        
        with col3:
            # Export career matrix as CSV
            if st.session_state.career_model.career_matrix:
                df = pd.DataFrame(
                    st.session_state.career_model.career_matrix, 
                    index=st.session_state.career_model.criteria_labels
                ).T
                csv = df.to_csv()
                st.download_button(
                    "📋 Career Matrix CSV",
                    data=csv,
                    file_name=f"career_matrix_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    key="export_csv"
                )
        
        with col4:
            # PDF Export
            if PDF_AVAILABLE and st.session_state.career_model.career_matrix:
                try:
                    pdf_buffer = generate_pdf_report(
                        st.session_state.career_model, 
                        st.session_state.history,
                        st.session_state.current_user_input
                    )
                    st.download_button(
                        "📄 Professional PDF",
                        data=pdf_buffer.getvalue(),
                        file_name=f"career_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        key="export_pdf"
                    )
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")
            else:
                st.info("📄 Install reportlab for PDF export")

    # --- Conversation History Section ---
    if st.session_state.history:
        st.divider()
        with st.expander("💭 Full Conversation History", expanded=False):
            for i, entry in enumerate(st.session_state.history):
                st.markdown(f"""
                <div style="background: #f8f9ff; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #667eea;">
                    <strong style="color: #667eea;">Q{i+1}:</strong> {entry['user']}
                </div>
                <div style="background: #ffffff; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #28a745;">
                    <strong style="color: #28a745;">A{i+1}:</strong> {entry['agent']}
                </div>
                """, unsafe_allow_html=True)
                if i < len(st.session_state.history) - 1:
                    st.markdown("---")

    # --- Professional Footer ---
    st.markdown("""
    <div class="footer">
        <h3 style="margin-bottom: 1rem;">🎯 AI Career Guide Professional</h3>
        <p style="margin: 0; opacity: 0.9;">
            Intelligent Career Guidance • Game Theory Analysis • Data-Driven Decisions
        </p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.7;">
            Making career decisions with mathematical precision and AI insights
        </p>
    </div>
    """, unsafe_allow_html=True)

# Allows running independently via `python app/ui_streamlit.py`
if __name__ == "__main__":
    main()