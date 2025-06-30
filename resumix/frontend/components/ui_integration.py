"""
Simple UI Integration for Resumix
Import this file to automatically apply modern UI styling
"""

from resumix.frontend.components.modern_ui import (
    ModernUI,
    modern_header,
    modern_card,
    modern_alert,
)
import streamlit as st
from typing import Literal

# Create UI instance but don't apply styles immediately
_ui_instance = None


def get_ui_instance():
    """Get or create the UI instance"""
    global _ui_instance
    if _ui_instance is None:
        _ui_instance = ModernUI(auto_apply=False)  # Don't apply styles on creation
    return _ui_instance


# Export commonly used functions for easy access
__all__ = ["get_ui_instance", "modern_header", "modern_card", "modern_alert"]


# Create an enhanced page config function
def setup_modern_page(
    page_title="Resumix", page_icon="📄", layout: Literal["centered", "wide"] = "wide"
):
    """Enhanced page config with modern UI"""
    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://github.com/resumix/help",
            "Report a bug": "https://github.com/resumix/issues",
            "About": "Resumix - AI-Powered Resume Assistant",
        },
    )

    # Apply modern UI styling after page config
    ui = get_ui_instance()
    return ui


# For backward compatibility, create ui_instance after ensuring it's safe
def _initialize_ui():
    """Initialize UI safely after page config"""
    try:
        return get_ui_instance()
    except:
        # If we can't initialize yet, return None
        return None


ui_instance = _initialize_ui()
