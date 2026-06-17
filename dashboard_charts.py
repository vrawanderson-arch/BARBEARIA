import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_advanced_dashboard(df_agendamentos):
    """Cria gráficos avançados para o dashboard usando Plotly"""
    
    if df_agendamentos.empty:
        return None, None, None

    # 1. Gráfico de Rosca: Status dos Agendamentos
    fig_status = px.pie(
        df_agendamentos, 
        names='status', 
        hole=0.4,
        title='Distribuição por Status',
        color_discrete_sequence=['#e91e8c', '#ffb3d9', '#cccccc']
    )
    fig_status.update_layout(showlegend=True)

    # 2. Gráfico de Barras: Receita Estimada por Serviço (Simulado)
    # Atribuindo valores fictícios para demonstração
    precos = {
        'Corte feminino': 80, 'Corte masculino': 40, 'Coloração': 150,
        'Manicure': 30, 'Pedicure': 30, 'Combo Mani + Pedi': 50,
        'Design de sobrancelha': 45, 'Escova progressiva': 250, 'Outro': 50
    }
    df_agendamentos['valor_estimado'] = df_agendamentos['servico'].map(precos).fillna(50)
    
    receita_servico = df_agendamentos.groupby('servico')['valor_estimado'].sum().reset_index()
    fig_receita = px.bar(
        receita_servico, 
        x='servico', 
        y='valor_estimado',
        title='Receita Estimada por Serviço (R$)',
        labels={'valor_estimado': 'Receita (R$)', 'servico': 'Serviço'},
        color='valor_estimado',
        color_continuous_scale='RdPu'
    )

    # 3. Gráfico de Linha: Evolução Temporal
    df_agendamentos['data_curta'] = pd.to_datetime(df_agendamentos['data']).dt.date
    evolucao = df_agendamentos.groupby('data_curta').size().reset_index(name='quantidade')
    fig_evolucao = px.line(
        evolucao, 
        x='data_curta', 
        y='quantidade',
        title='Evolução de Agendamentos',
        markers=True
    )
    fig_evolucao.update_traces(line_color='#e91e8c')

    return fig_status, fig_receita, fig_evolucao
