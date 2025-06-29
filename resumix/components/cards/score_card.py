import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from typing import Dict, Any, Optional, Tuple, List
from components.cards.base_card import BaseCard
from loguru import logger

class ScoreCard(BaseCard):
    def __init__(self, section_name: str, scores: dict):
        """
        Initialize a ScoreCard with section name and scores.
        
        Args:
            section_name: Name of the resume section being scored
            scores: Dictionary containing score dimensions and values
                   Example: {"完整性": 8, "清晰度": 7, "Comment": "Good section"}
        """
        # Extract comment from scores (support both English and Chinese)
        comment = scores.get("Comment") or scores.get("评语") or "No comment provided."
        
        # Initialize BaseCard with title, icon and comment
        super().__init__(
            title=f"Score for {section_name}",
            icon="📊",
            comment=comment
        )
        
        # Store numeric scores only (filter out non-numeric items)
        self.score_items = {
            k: v for k, v in scores.items() if isinstance(v, (int, float))
        }
        self.section_name = section_name
        
        # Configure matplotlib for Chinese characters if needed
        self._configure_matplotlib()

    def _configure_matplotlib(self):
        """Configure matplotlib settings for proper display"""
        matplotlib.rcParams["font.family"] = "Arial"
        matplotlib.rcParams["axes.unicode_minus"] = False

    def _prepare_radar_data(self):
        """Prepare data for radar chart visualization"""
        labels = list(self.score_items.keys())
        values = list(self.score_items.values())
        
        # Close the radar chart loop
        values += values[:1]
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]
        
        return labels, values, angles

    def render_radar_chart(self):
        """Render a radar chart visualization of the scores"""
        try:
            labels, values, angles = self._prepare_radar_data()
            
            fig = plt.figure(figsize=(3.5, 3.5))
            ax = fig.add_subplot(111, polar=True)
            ax.plot(angles, values, linewidth=2)
            ax.fill(angles, values, alpha=0.25)
            ax.set_thetagrids(
                [angle * 180 / np.pi for angle in angles[:-1]],
                labels
            )
            ax.set_ylim(0, 10)
            st.pyplot(fig, clear_figure=True)
        except Exception as e:
            logger.error(f"Failed to render radar chart: {e}")
            st.warning("Could not display score visualization")

    def render_score_table(self):
        """Render a table view of the scores"""
        try:
            df = pd.DataFrame(
                {
                    "Dimension": list(self.score_items.keys()),
                    "Score": list(self.score_items.values()),
                }
            )
            st.dataframe(
                df.set_index("Dimension"),
                use_container_width=True,
                height=180
            )
        except Exception as e:
            logger.error(f"Failed to render score table: {e}")
            st.warning("Could not display score table")

    def render_comment(self):
        """Render the comment section"""
        if self.comment:
            st.markdown(f"*📊 {self.comment}*")

    def render_card_body(self):
        """
        Render the main score card content with clean text hierarchy.
        """
        try:
            st.markdown("### 📊 Resume Scoring")
            
            # Check if we have scoring data
            scores = st.session_state.get("resume_scores", {})
            
            if not scores:
                st.info("📊 Upload a resume and add a job description to see detailed scoring")
                return
            
            # Simple two-column layout for chart and table
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("#### 📈 Score Visualization")
                self.render_radar_chart()
                
            with col2:
                st.markdown("#### 📋 Score Details")
                self.render_score_table()
                
        except Exception as e:
            logger.error(f"Failed to render score card body: {e}")
            st.error("Could not display scoring interface")

    def render(self):
        """
        Simple render method using the clean BaseCard structure.
        """
        logger.info("Rendering ScoreCard")
        
        # Use the simplified BaseCard render method
        super().render()