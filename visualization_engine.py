"""
Visualization Engine Module
Plotly-based chart generation for EDA
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import json


class VisualizationEngine:
    """Generate Plotly visualizations for EDA"""
    
    # Color palette matching the UI theme
    COLORS = {
        'primary': '#3B5998',
        'secondary': '#00ACC1',
        'accent': '#FF6D00',
        'success': '#4CAF50',
        'warning': '#FF9800',
        'danger': '#F44336',
        'info': '#2196F3',
        'palette': [
            '#3B5998', '#00ACC1', '#FF6D00', '#9C27B0', 
            '#4CAF50', '#FF5722', '#607D8B', '#E91E63',
            '#00BCD4', '#8BC34A', '#FFC107', '#795548'
        ]
    }
    
    # Dark mode colors
    DARK_COLORS = {
        'bg': '#1A1F3C',
        'paper': '#252B48',
        'text': '#E2E8F0',
        'grid': '#3D4566'
    }
    
    # Light mode colors
    LIGHT_COLORS = {
        'bg': '#F5F7FA',
        'paper': '#FFFFFF',
        'text': '#2D3748',
        'grid': '#E2E8F0'
    }
    
    @classmethod
    def get_layout(cls, title: str, dark_mode: bool = False) -> Dict:
        """Get consistent layout for charts"""
        colors = cls.DARK_COLORS if dark_mode else cls.LIGHT_COLORS
        
        return {
            'title': {
                'text': title,
                'font': {'size': 18, 'color': colors['text']},
                'x': 0.5,
                'xanchor': 'center'
            },
            'paper_bgcolor': colors['paper'],
            'plot_bgcolor': colors['bg'],
            'font': {'color': colors['text'], 'family': 'Inter, system-ui, sans-serif'},
            'margin': {'l': 60, 'r': 40, 't': 60, 'b': 60},
            'xaxis': {
                'gridcolor': colors['grid'],
                'zerolinecolor': colors['grid']
            },
            'yaxis': {
                'gridcolor': colors['grid'],
                'zerolinecolor': colors['grid']
            },
            'legend': {
                'bgcolor': 'rgba(0,0,0,0)',
                'font': {'color': colors['text']}
            }
        }
    
    @classmethod
    def create_bar_chart(
        cls,
        df: pd.DataFrame,
        x: str,
        y: str,
        title: str = "Bar Chart",
        color: str = None,
        dark_mode: bool = False
    ) -> str:
        """Create a bar chart"""
        fig = px.bar(
            df,
            x=x,
            y=y,
            color=color,
            color_discrete_sequence=cls.COLORS['palette'],
            title=title
        )
        fig.update_layout(**cls.get_layout(title, dark_mode))
        return fig.to_json()
    
    @classmethod
    def create_line_chart(
        cls,
        df: pd.DataFrame,
        x: str,
        y: str,
        title: str = "Line Chart",
        color: str = None,
        dark_mode: bool = False
    ) -> str:
        """Create a line chart"""
        fig = px.line(
            df,
            x=x,
            y=y,
            color=color,
            color_discrete_sequence=cls.COLORS['palette'],
            title=title,
            markers=True
        )
        fig.update_layout(**cls.get_layout(title, dark_mode))
        return fig.to_json()
    
    @classmethod
    def create_histogram(
        cls,
        df: pd.DataFrame,
        column: str,
        bins: int = 30,
        title: str = None,
        dark_mode: bool = False
    ) -> str:
        """Create a histogram"""
        if title is None:
            title = f"Distribution of {column}"
        
        fig = px.histogram(
            df,
            x=column,
            nbins=bins,
            color_discrete_sequence=[cls.COLORS['primary']],
            title=title
        )
        
        # Add mean line
        mean_val = df[column].mean()
        fig.add_vline(
            x=mean_val,
            line_dash="dash",
            line_color=cls.COLORS['accent'],
            annotation_text=f"Mean: {mean_val:.2f}"
        )
        
        fig.update_layout(**cls.get_layout(title, dark_mode))
        return fig.to_json()
    
    @classmethod
    def create_box_plot(
        cls,
        df: pd.DataFrame,
        columns: List[str] = None,
        title: str = "Box Plot",
        dark_mode: bool = False
    ) -> str:
        """Create a box plot"""
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()[:10]
        
        fig = go.Figure()
        
        for i, col in enumerate(columns):
            fig.add_trace(go.Box(
                y=df[col],
                name=col,
                marker_color=cls.COLORS['palette'][i % len(cls.COLORS['palette'])]
            ))
        
        fig.update_layout(**cls.get_layout(title, dark_mode))
        return fig.to_json()
    
    @classmethod
    def create_correlation_heatmap(
        cls,
        df: pd.DataFrame,
        title: str = "Correlation Matrix",
        dark_mode: bool = False
    ) -> str:
        """Create a correlation heatmap"""
        numeric_df = df.select_dtypes(include=[np.number])
        corr_matrix = numeric_df.corr()
        
        fig = px.imshow(
            corr_matrix,
            text_auto='.2f',
            aspect='auto',
            color_continuous_scale='RdBu_r',
            title=title
        )
        
        fig.update_layout(**cls.get_layout(title, dark_mode))
        return fig.to_json()
    
    @classmethod
    def create_scatter_plot(
        cls,
        df: pd.DataFrame,
        x: str,
        y: str,
        color: str = None,
        size: str = None,
        title: str = "Scatter Plot",
        dark_mode: bool = False
    ) -> str:
        """Create a scatter plot"""
        fig = px.scatter(
            df,
            x=x,
            y=y,
            color=color,
            size=size,
            color_discrete_sequence=cls.COLORS['palette'],
            title=title
        )
        
        # Add trendline
        fig.update_traces(marker=dict(opacity=0.7))
        
        fig.update_layout(**cls.get_layout(title, dark_mode))
        return fig.to_json()
    
    @classmethod
    def create_pie_chart(
        cls,
        df: pd.DataFrame,
        names: str,
        values: str,
        title: str = "Pie Chart",
        dark_mode: bool = False
    ) -> str:
        """Create a pie chart"""
        fig = px.pie(
            df,
            names=names,
            values=values,
            color_discrete_sequence=cls.COLORS['palette'],
            title=title,
            hole=0.4
        )
        
        fig.update_layout(**cls.get_layout(title, dark_mode))
        return fig.to_json()
    
    @classmethod
    def create_missing_value_chart(
        cls,
        missing_data: Dict[str, Any],
        title: str = "Missing Values by Column",
        dark_mode: bool = False
    ) -> str:
        """Create a bar chart showing missing values"""
        columns = list(missing_data['by_column'].keys())
        percentages = [missing_data['by_column'][col]['percentage'] for col in columns]
        
        # Sort by percentage descending
        sorted_data = sorted(zip(columns, percentages), key=lambda x: x[1], reverse=True)
        columns, percentages = zip(*sorted_data) if sorted_data else ([], [])
        
        # Color based on severity
        colors = []
        for pct in percentages:
            if pct == 0:
                colors.append(cls.COLORS['success'])
            elif pct < 10:
                colors.append(cls.COLORS['info'])
            elif pct < 30:
                colors.append(cls.COLORS['warning'])
            else:
                colors.append(cls.COLORS['danger'])
        
        fig = go.Figure(go.Bar(
            x=list(columns)[:20],  # Limit to 20 columns
            y=list(percentages)[:20],
            marker_color=colors[:20],
            text=[f"{p:.1f}%" for p in percentages[:20]],
            textposition='outside'
        ))
        
        fig.update_layout(**cls.get_layout(title, dark_mode))
        fig.update_layout(yaxis_title="Missing %", xaxis_tickangle=-45)
        return fig.to_json()
    
    @classmethod
    def create_distribution_grid(
        cls,
        df: pd.DataFrame,
        columns: List[str] = None,
        dark_mode: bool = False
    ) -> str:
        """Create a grid of distribution plots"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if columns:
            numeric_cols = [c for c in columns if c in numeric_cols]
        
        # Limit to first 6 columns
        numeric_cols = numeric_cols[:6]
        
        if not numeric_cols:
            return json.dumps({})
        
        rows = (len(numeric_cols) + 1) // 2
        fig = make_subplots(rows=rows, cols=2, subplot_titles=numeric_cols)
        
        for i, col in enumerate(numeric_cols):
            row = i // 2 + 1
            col_idx = i % 2 + 1
            
            fig.add_trace(
                go.Histogram(
                    x=df[col],
                    name=col,
                    marker_color=cls.COLORS['palette'][i],
                    showlegend=False
                ),
                row=row,
                col=col_idx
            )
        
        layout = cls.get_layout("Distribution Overview", dark_mode)
        layout['height'] = 200 * rows
        fig.update_layout(**layout)
        return fig.to_json()
    
    @classmethod
    def create_summary_stats_chart(
        cls,
        stats: Dict[str, Any],
        columns: List[str] = None,
        dark_mode: bool = False
    ) -> str:
        """Create a summary statistics comparison chart"""
        if columns is None:
            columns = [k for k in stats.keys() if 'mean' in stats.get(k, {})][:8]
        
        if not columns:
            return json.dumps({})
        
        metrics = ['min', 'q1', 'median', 'q3', 'max']
        
        fig = go.Figure()
        
        for i, col in enumerate(columns):
            if col in stats and all(m in stats[col] for m in metrics):
                col_stats = stats[col]
                fig.add_trace(go.Box(
                    name=col,
                    q1=[col_stats['q1']],
                    median=[col_stats['median']],
                    q3=[col_stats['q3']],
                    lowerfence=[col_stats['min']],
                    upperfence=[col_stats['max']],
                    marker_color=cls.COLORS['palette'][i % len(cls.COLORS['palette'])]
                ))
        
        fig.update_layout(**cls.get_layout("Statistical Summary", dark_mode))
        return fig.to_json()
