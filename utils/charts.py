import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

PALETTE = ['#00F5C4','#7C3AED','#F59E0B','#F87171','#60A5FA','#34D399','#A78BFA','#FCA5A5']
TEMPLATE = dict(
    layout=dict(
        paper_bgcolor='#111827',
        plot_bgcolor='#111827',
        font=dict(color='#E2E8F0', family='DM Sans'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)', zerolinecolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', zerolinecolor='rgba(255,255,255,0.1)'),
        title=dict(font=dict(size=17, color='#E2E8F0')),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8')),
        hoverlabel=dict(bgcolor='#1a2235', bordercolor='#00F5C4', font=dict(color='#E2E8F0')),
        margin=dict(t=50, l=20, r=20, b=20),
    )
)


def make_charts(df: pd.DataFrame, ai_analysis: dict) -> list:
    charts = []

    num_cols = [c for c in (ai_analysis.get('numeric_columns') or []) if c in df.columns]
    cat_cols = [c for c in (ai_analysis.get('category_columns') or []) if c in df.columns]
    date_col = ai_analysis.get('date_column')
    if date_col and date_col not in df.columns:
        date_col = None

    if not num_cols:
        num_cols = list(df.select_dtypes(include=[np.number]).columns)
    if not cat_cols:
        cat_cols = [c for c in df.select_dtypes(include='object').columns if df[c].nunique() < 30]

    # 1 ── Time Series
    if date_col and num_cols:
        try:
            cols = num_cols[:2]
            dft = df[[date_col]+cols].dropna().sort_values(date_col)
            fig = go.Figure()
            for i, col in enumerate(cols):
                fig.add_trace(go.Scatter(
                    x=dft[date_col], y=dft[col], name=col,
                    mode='lines+markers',
                    line=dict(color=PALETTE[i], width=2.5, shape='spline'),
                    marker=dict(size=4, color=PALETTE[i]),
                    fill='tozeroy' if i == 0 else 'none',
                    fillcolor=f'rgba(0,245,196,0.05)' if i == 0 else None
                ))
            fig.update_layout(**TEMPLATE['layout'],
                title="📈 Trend Over Time", hovermode='x unified',
                legend=dict(orientation='h', yanchor='bottom', y=1.02))
            charts.append(fig)
        except Exception:
            pass

    # 2 ── Bar Chart
    if cat_cols and num_cols:
        try:
            cat, num = cat_cols[0], num_cols[0]
            dfb = df.groupby(cat)[num].sum().reset_index().sort_values(num, ascending=False).head(15)
            fig = go.Figure(go.Bar(
                x=dfb[cat], y=dfb[num],
                marker=dict(
                    color=dfb[num],
                    colorscale=[[0,'#7C3AED'],[0.5,'#00F5C4'],[1,'#F59E0B']],
                    line=dict(width=0)
                ),
                hovertemplate=f'<b>%{{x}}</b><br>{num}: %{{y:,.0f}}<extra></extra>'
            ))
            fig.update_layout(**TEMPLATE['layout'], title=f"📊 {num} by {cat}")
            charts.append(fig)
        except Exception:
            pass

    # 3 ── Donut Chart
    if cat_cols and num_cols:
        try:
            cat, num = cat_cols[0], num_cols[0]
            if df[cat].nunique() <= 12:
                dfp = df.groupby(cat)[num].sum().reset_index()
                fig = go.Figure(go.Pie(
                    labels=dfp[cat], values=dfp[num],
                    hole=0.5,
                    marker=dict(colors=PALETTE, line=dict(color='#0A0E1A', width=2)),
                    textfont=dict(color='#E2E8F0'),
                    hovertemplate='<b>%{label}</b><br>%{value:,.0f} (%{percent})<extra></extra>'
                ))
                fig.update_layout(**TEMPLATE['layout'], title=f"🥧 {num} Distribution")
                charts.append(fig)
        except Exception:
            pass

    # 4 ── Histogram
    if num_cols:
        try:
            col = num_cols[0]
            fig = go.Figure(go.Histogram(
                x=df[col], nbinsx=30,
                marker=dict(color='#00F5C4', opacity=0.8,
                            line=dict(color='#0A0E1A', width=1)),
                hovertemplate=f'{col}: %{{x}}<br>Count: %{{y}}<extra></extra>'
            ))
            fig.update_layout(**TEMPLATE['layout'], title=f"📉 Distribution of {col}")
            charts.append(fig)
        except Exception:
            pass

    # 5 ── Correlation Heatmap
    if len(num_cols) >= 3:
        try:
            corr = df[num_cols[:8]].corr()
            fig = go.Figure(go.Heatmap(
                z=corr.values, x=corr.columns, y=corr.columns,
                colorscale=[[0,'#7C3AED'],[0.5,'#111827'],[1,'#00F5C4']],
                zmin=-1, zmax=1,
                text=corr.values.round(2), texttemplate='%{text}',
                textfont=dict(size=10),
                showscale=True,
                hoverongaps=False
            ))
            fig.update_layout(**TEMPLATE['layout'], title="🔗 Correlation Matrix")
            charts.append(fig)
        except Exception:
            pass

    return charts
