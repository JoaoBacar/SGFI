import streamlit as st
import pandas as pd
import os
from conexao import conectar
from ddl_dml import criar_e_popular_banco, eliminar_todas_tabelas
from crud import TABELAS
from relatorios_graficos import CONSULTAS

st.set_page_config(page_title="SGFI - Gestão de Filas Inteligente", page_icon="⏱️", layout="wide")

# --- ESTILO VISUAL DO LOGOTIPO SGFI --
st.markdown("""
    <style>
    /* Títulos em Azul  */
    h1, h2, h3 {
        color: #123C5A !important;
    }
    /* Linha decorativa no cabeçalho */
    .header-divider {
        height: 4px;
        background: linear-gradient(90deg, #123C5A 0%, #1A8FE3 60%, #10B981 100%);
        border-radius: 2px;
        margin-bottom: 20px;
    }
    /* Estilização dos botões */
    div.stButton > button {
        background-color: #123C5A;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
    }
    div.stButton > button:hover {
        background-color: #1A8FE3;
        color: white;
    }
    /* Destaque das abas selecionadas */
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #1A8FE3 !important;
        border-bottom-color: #10B981 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- LOGOTIPO NA BARRA LATERAL ---
if os.path.exists("logo_sgfi.png"):
    st.sidebar.image("logo_sgfi.png", use_container_width=True)
elif os.path.exists("logo_sgfi.jpg"):
    st.sidebar.image("logo_sgfi.jpg", use_container_width=True)

st.sidebar.markdown("---")

# --- CABEÇALHO PRINCIPAL ---
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    if os.path.exists("logo_sgfi.png"):
        st.image("logo_sgfi.png", width=130)
    elif os.path.exists("logo_sgfi.jpg"):
        st.image("logo_sgfi.jpg", width=130)
with col_titulo:
    st.title("SGFI — Sistema de Gestão de Filas Inteligente")
    st.caption("Controle Operacional, Indicadores Analíticos e Apoio à Decisão com IA Generativa")

st.markdown('<div class="header-divider"></div>', unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Navegação",
    [
        "1. Banco de Dados (Criar / Apagar)",
        "2. Gerenciar Tabelas (CRUD)",
        "3. Consultas e Gráficos (Item 6)",
        "4. Assistente IA Generativa"
    ]
)

# --- 1. DDL + DML / DROP (Item 7.e) ---
if menu == "1. Banco de Dados (Criar / Apagar)":
    st.header("Administração da Estrutura do Banco")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Criação Tabelas E Carregamento de Dados ", use_container_width=True):
            try:
                criar_e_popular_banco()
                st.success("Banco 'SGFI' criado e populado com sucesso!")
            except Exception as e:
                st.error(f"Erro: {e}")
    with col2:
        if st.button("Eliminar Todas as Tabelas (DROP TABLES)", type="primary", use_container_width=True):
            try:
                eliminar_todas_tabelas()
                st.warning("Todas as tabelas foram removidas do banco 'SGFI'.")
            except Exception as e:
                st.error(f"Erro: {e}")

# --- 2. CRUD COMPLETO (Item 7.b) ---
elif menu == "2. Gerenciar Tabelas (CRUD)":
    st.header("Operações CRUD em Todas as Tabelas")
    tabela = st.selectbox("Selecione a tabela:", TABELAS)

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(f"SHOW COLUMNS FROM {tabela};")
    colunas_info = cursor.fetchall()
    todas_cols = [c[0] for c in colunas_info if "GENERATED" not in c[5]]
    pks = [c[0] for c in colunas_info if c[3] == "PRI"]
    editaveis = [c[0] for c in colunas_info if "auto_increment" not in c[5] and "GENERATED" not in c[5]]

    aba_consulta, aba_inserir, aba_atualizar, aba_excluir = st.tabs(
        ["🔍 Consultar", "➕ Inserir", "✏️ Atualizar", "❌ Excluir"]
    )

    with aba_consulta:
        cursor.execute(f"SELECT {', '.join(todas_cols)} FROM {tabela};")
        df = pd.DataFrame(cursor.fetchall(), columns=todas_cols)
        st.dataframe(df, use_container_width=True)

    with aba_inserir:
        with st.form("form_insert"):
            valores = {}
            for col in editaveis:
                valores[col] = st.text_input(f"{col} (deixe vazio para NULL/DEFAULT)")
            if st.form_submit_button("Salvar Registro"):
                try:
                    cols_ok = [k for k, v in valores.items() if v.strip() != ""]
                    vals_ok = [v.strip() for v in valores.values() if v.strip() != ""]
                    sql = f"INSERT INTO {tabela} ({', '.join(cols_ok)}) VALUES ({', '.join(['%s']*len(vals_ok))});"
                    cursor.execute(sql, vals_ok)
                    conn.commit()
                    st.success("Registro inserido! Atualize a aba Consultar.")
                except Exception as e:
                    st.error(f"Erro de integridade/SQL: {e}")

    with aba_atualizar:
        with st.form("form_update"):
            pk_vals = {pk: st.text_input(f"Chave Primária ({pk})") for pk in pks}
            col_alvo = st.selectbox("Coluna a alterar:", editaveis)
            novo_val = st.text_input("Novo valor:")
            if st.form_submit_button("Atualizar"):
                try:
                    where_sql = " AND ".join([f"{k} = %s" for k in pks])
                    sql = f"UPDATE {tabela} SET {col_alvo} = %s WHERE {where_sql};"
                    cursor.execute(sql, [novo_val.strip()] + [v.strip() for v in pk_vals.values()])
                    conn.commit()
                    st.success(f"{cursor.rowcount} registro(s) atualizado(s)!")
                except Exception as e:
                    st.error(f"Erro: {e}")

    with aba_excluir:
        with st.form("form_delete"):
            pk_del = {pk: st.text_input(f"Chave Primária para excluir ({pk})") for pk in pks}
            if st.form_submit_button("Excluir Registro"):
                try:
                    where_sql = " AND ".join([f"{k} = %s" for k in pks])
                    sql = f"DELETE FROM {tabela} WHERE {where_sql};"
                    cursor.execute(sql, [v.strip() for v in pk_del.values()])
                    conn.commit()
                    st.success(f"{cursor.rowcount} registro(s) excluído(s)!")
                except Exception as e:
                    st.error(f"Erro (verifique chaves estrangeiras): {e}")

    cursor.close()
    conn.close()

# --- 3. CONSULTAS E GRÁFICOS (Item 7.c) ---
elif menu == "3. Consultas e Gráficos":
    st.header("Relatórios Gerenciais e Gráficos")
    escolha = st.selectbox(
        "Escolha a consulta:",
        ["1", "2", "3"],
        format_func=lambda k: f"Consulta {k}: {CONSULTAS[k]['titulo']}"
    )
    item = CONSULTAS[escolha]
    conn = conectar()
    df_res = pd.read_sql(item["sql"], conn)
    conn.close()

    col_tab, col_graf = st.columns([1, 1.3])
    with col_tab:
        st.subheader("Tabela de Resultados")
        st.dataframe(df_res, use_container_width=True)
    with col_graf:
        st.subheader("Gráfico")
        if not df_res.empty:
            st.bar_chart(df_res.set_index(df_res.columns[0])[df_res.columns[1]], color="#1A8FE3")

# --- 4. IA GENERATIVA (Item 7.f) ---
elif menu == "4. Assistente IA Generativa":
    st.header("Diagnóstico Operacional com IA Generativa (Gemini)")
    api_key = st.text_input("Sua GEMINI_API_KEY:", type="password")
    if st.button("Analisar Filas e Produtividade"):
        if not api_key:
            st.warning("Informe sua chave da API do Gemini.")
        else:
            from google import genai
            conn = conectar()
            df_esp = pd.read_sql(CONSULTAS["2"]["sql"], conn)
            df_atd = pd.read_sql(CONSULTAS["3"]["sql"], conn)
            conn.close()

            prompt = f"""
            Analise estes indicadores reais de um Sistema de Gestão de Filas (SGFI):
- Tempo médio de espera por unidade: {df_esp.to_dict(orient='records')}
- Produtividade e avaliação por atendente: {df_atd.to_dict(orient='records')}
            Dê 3 recomendações práticas para o gestor melhorar o atendimento.
            """
            with st.spinner("Consultando Gemini..."):
                client = genai.Client(
                    api_key=api_key,
                    http_options={"api_version": "v1beta"}
                )
                sucesso = False
                for m in ["gemini-3.1-flash-lite-preview", "gemini-3-flash-preview", "gemini-3.1-pro-preview"]:
                    try:
                        resp = client.models.generate_content(model=m, contents=prompt)
                        st.markdown(resp.text)
                        sucesso = True
                        break
                    except Exception as e:
                        erro_msg = str(e)
                if not sucesso:
                    st.error(f"Erro na API: {erro_msg}")