"""
Modern UI/UX Styling for Resumix Application
Inspired by ChatGPT and DeepSeek design principles
"""

import streamlit as st
from typing import Optional

class ModernUI:
    """Modern UI styling and components for Resumix"""
    
    def __init__(self, auto_apply: bool = True):
        self._styles_applied = False
        if auto_apply:
            self.apply_global_styles()
    
    def apply_global_styles(self):
        """Apply modern global CSS styling"""
        if self._styles_applied:
            return
        
        self._styles_applied = True
        st.markdown("""
        <style>
        /* Import modern fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global variables for modern color scheme */
        :root {
            --primary-color: #1f9f83;
            --primary-hover: #0f7a63;
            --secondary-color: #64748b;
            --accent-color: #06b6d4;
            --success-color: #1f9f83;
            --warning-color: #f59e0b;
            --error-color: #1f9f83;
            --background-light: #ffffff;
            --background-dark: #0f172a;
            --surface-light: #f8fafc;
            --surface-dark: #1e293b;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --shadow-light: 0 1px 3px 0 rgb(0 0 0 / 0.1);
            --shadow-medium: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            --shadow-large: 0 20px 25px -5px rgb(0 0 0 / 0.1);
        }
        
        /* Main app container */
        .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #ffffff;
            min-height: 100vh;
        }
        
        /* Main content area */
        .main .block-container {
            background: var(--background-light);
            border-radius: 16px;
            box-shadow: var(--shadow-large);
            padding: 2rem;
            margin: 1rem;
            max-width: 1200px;
        }
        
        /* Header styling */
        .stApp > header {
            background: transparent;
            height: 0;
        }
        
        /* Sidebar modern styling */
        .sidebar .sidebar-content {
            background: var(--surface-light);
            border-radius: 12px;
            box-shadow: var(--shadow-medium);
            padding: 1rem;
        }
        
        /* Modern button styling */
        .stButton > button {
            background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            font-size: 0.875rem;
            transition: all 0.2s ease;
            box-shadow: var(--shadow-light);
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: var(--shadow-medium);
            background: linear-gradient(135deg, var(--primary-hover), var(--primary-color));
        }
        
        /* File uploader styling */
        .stFileUploader {
            background: var(--surface-light);
            border: 2px dashed var(--border-color);
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            transition: all 0.2s ease;
        }
        
        .stFileUploader:hover {
            border-color: var(--primary-color);
            background: rgba(16, 185, 129, 0.05);
        }
        
        /* Input field styling */
        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 1px solid var(--border-color);
            padding: 0.75rem 1rem;
            font-size: 0.875rem;
            transition: all 0.2s ease;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            background: var(--surface-light);
            border-radius: 12px;
            padding: 0.25rem;
            gap: 0.25rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border-radius: 8px;
            color: var(--text-secondary);
            font-weight: 500;
            padding: 0.75rem 1.5rem;
            transition: all 0.2s ease;
        }
        
        .stTabs [aria-selected="true"] {
            background: white;
            color: var(--primary-color);
            box-shadow: var(--shadow-light);
        }
        
        /* Card-like containers */
        .element-container {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: var(--shadow-light);
            border: 1px solid var(--border-color);
        }
        
        /* Modern alerts */
        .stAlert {
            border-radius: 8px;
            border: none;
            padding: 1rem 1.5rem;
            margin: 1rem 0;
        }
        
        .stAlert[data-baseweb="notification"] {
            background: rgba(16, 185, 129, 0.1);
            color: var(--success-color);
        }
        
        /* Progress bar */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
            border-radius: 4px;
        }
        
        /* Metrics styling */
        .metric-container {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: var(--shadow-light);
            border: 1px solid var(--border-color);
            transition: all 0.2s ease;
        }
        
        .metric-container:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-medium);
        }
        
        /* Chat message styling */
        .stChatMessage {
            background: var(--surface-light);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            margin: 0.5rem 0;
            border: 1px solid var(--border-color);
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background: var(--surface-light);
            border-radius: 8px;
            border: 1px solid var(--border-color);
            padding: 0.75rem 1rem;
            font-weight: 500;
        }
        
        /* Modern scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--surface-light);
            border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--secondary-color);
            border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-secondary);
        }
        
        /* Loading spinner */
        .stSpinner {
            border-color: var(--primary-color);
        }
        
        /* Modern typography */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-primary);
            font-weight: 600;
            letter-spacing: -0.025em;
        }
        
        p {
            color: var(--text-secondary);
            line-height: 1.6;
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            :root {
                --background-light: var(--background-dark);
                --surface-light: var(--surface-dark);
                --text-primary: #f1f5f9;
                --text-secondary: #94a3b8;
                --border-color: #334155;
            }
        }
        </style>
        """, unsafe_allow_html=True)
    
    def create_modern_header(self, title: str, subtitle: Optional[str] = None, icon: str = "🚀"):
        """Create a modern header section"""
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem 0;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">{icon}</div>
            <h1 style="font-size: 2.5rem; font-weight: 700; color: #1e293b; margin: 0;">{title}</h1>
            {f'<p style="font-size: 1.125rem; color: #64748b; margin-top: 0.5rem;">{subtitle}</p>' if subtitle else ''}
        </div>
        """, unsafe_allow_html=True)
    
    def create_feature_card(self, title: str, description: str, icon: str, color: str = "#10b981"):
        """Create a modern feature card"""
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            border: 1px solid #e2e8f0;
            text-align: center;
            transition: all 0.2s ease;
            height: 100%;
        ">
            <div style="
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, {color}, {color}dd);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1rem;
                font-size: 1.5rem;
            ">{icon}</div>
            <h3 style="font-size: 1.25rem; font-weight: 600; color: #1e293b; margin-bottom: 0.5rem;">{title}</h3>
            <p style="color: #64748b; line-height: 1.6; margin: 0;">{description}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def create_stats_card(self, value: str, label: str, icon: str, color: str = "#10b981"):
        """Create a modern statistics card"""
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
            border-left: 4px solid {color};
            text-align: center;
        ">
            <div style="color: {color}; font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
            <div style="font-size: 2rem; font-weight: 700; color: #1e293b; margin-bottom: 0.25rem;">{value}</div>
            <div style="color: #64748b; font-size: 0.875rem; font-weight: 500;">{label}</div>
        </div>
        """, unsafe_allow_html=True)
    
    def create_modern_section(self, title: str, content: str, icon: str = "📋"):
        """Create a modern content section"""
        with st.container():
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
                border: 1px solid #e2e8f0;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <span style="font-size: 1.25rem; margin-right: 0.5rem;">{icon}</span>
                    <h2 style="font-size: 1.25rem; font-weight: 600; color: #1e293b; margin: 0;">{title}</h2>
                </div>
                <div style="color: #64748b; line-height: 1.6;">
                    {content}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def create_modern_alert(self, message: str, alert_type: str = "info"):
        """Create modern alert messages"""
        colors = {
            "info": {"bg": "#d1fae5", "border": "#10b981", "icon": "ℹ️"},
            "success": {"bg": "#d1fae5", "border": "#10b981", "icon": "✅"},
            "warning": {"bg": "#fef3c7", "border": "#f59e0b", "icon": "⚠️"},
            "error": {"bg": "#d1fae5", "border": "#10b981", "icon": "❌"}
        }
        
        color_scheme = colors.get(alert_type, colors["info"])
        
        st.markdown(f"""
        <div style="
            background: {color_scheme['bg']};
            border-left: 4px solid {color_scheme['border']};
            border-radius: 8px;
            padding: 1rem 1.5rem;
            margin: 1rem 0;
            display: flex;
            align-items: center;
        ">
            <span style="font-size: 1.25rem; margin-right: 0.75rem;">{color_scheme['icon']}</span>
            <div style="color: #374151; font-weight: 500;">{message}</div>
        </div>
        """, unsafe_allow_html=True)
    
    def create_loading_spinner(self, text: str = "Processing..."):
        """Create a modern loading spinner"""
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
        ">
            <div style="
                width: 20px;
                height: 20px;
                border: 2px solid #e2e8f0;
                border-top: 2px solid #2563eb;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 0.75rem;
            "></div>
            <span style="color: #64748b; font-weight: 500;">{text}</span>
        </div>
        <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        </style>
        """, unsafe_allow_html=True)


# Initialize modern UI
def apply_modern_ui():
    """Apply modern UI styling to the Streamlit app"""
    return ModernUI()


# Utility functions for easy use
def modern_header(title: str, subtitle: Optional[str] = None, icon: str = "🚀"):
    """Quick function to add modern header"""
    ui = ModernUI()
    ui.create_modern_header(title, subtitle, icon)


def modern_card(title: str, description: str, icon: str, color: str = "#2563eb"):
    """Quick function to add feature card"""
    ui = ModernUI()
    ui.create_feature_card(title, description, icon, color)


def modern_alert(message: str, alert_type: str = "info"):
    """Quick function to add modern alert"""
    ui = ModernUI()
    ui.create_modern_alert(message, alert_type) 