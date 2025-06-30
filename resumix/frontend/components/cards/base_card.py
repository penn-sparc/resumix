# file: components/cards/base_card.py

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from typing import Dict, Optional, List
from resumix.shared.utils.logger import logger
from abc import ABC, abstractmethod


class BaseCard(ABC):
    def __init__(
        self,
        title: str,
        icon: str = "",
        comment: Optional[str] = None,
        additional_content: Optional[str] = None,
    ):
        self.title = title
        self.icon = icon
        self.comment = comment
        self.additional_content = additional_content

        # 设置统一字体风格（可封装为 theme）
        # matplotlib.rcParams["font.family"] = "PingFang SC"
        matplotlib.rcParams["axes.unicode_minus"] = False

    def render(self):
        """
        Simplified render method with clean text hierarchy.
        Template method pattern - calls render_card_body() for specific content.
        """
        try:
            # Simple header with emoji and title
            if self.icon:
                st.markdown(f"## {self.icon} {self.title}")
            else:
                st.markdown(f"## {self.title}")
            
            # Render main content
            self.render_card_body()
            
            # Render comment if available
            if self.comment:
                st.markdown(f"*{self.comment}*")
                
            # Render additional content if available
            if self.additional_content:
                st.markdown(self.additional_content)
                
        except Exception as e:
            logger.error(f"Failed to render {self.__class__.__name__}: {e}")
            st.error(f"Error rendering {self.title}")

    @abstractmethod
    def render_card_body(self):
        """
        Abstract method for rendering the main card content.
        Each card implements this method for its specific content.
        """
        pass

    def render_comment(self):
        """Default comment rendering - can be overridden by child classes"""
        if self.comment:
            st.markdown(f"*�� {self.comment}*")
