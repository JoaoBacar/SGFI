import os
from google import genai
from conexao import conectar

def analisar_operacao_com_ia():
    api_key = ""
    if not api_key:
        print("[AVISO] Chave de API não informada.")
        return

    # Busca dados reais do banco para dar contexto ao LLM
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.nome_unid, ROUND(AVG(ef.tempo_estimad), 1)
        FROM unidade u
        JOIN unidade_servico us ON u.id_unidade = us.id_unidade
        JOIN servico_fila sf ON us.id_servico = sf.id_servico
        JOIN entra_fila ef ON sf.id_fila = ef.id_fila
        GROUP BY u.nome_unid;
    """)
    dados_espera = cursor.fetchall()

    cursor.execute("""
        SELECT at.nome, COUNT(a.id_atendimento), ROUND(AVG(av.nota), 2)
        FROM atendente at
        JOIN atendimento a ON at.id_atendente = a.id_atendente
        LEFT JOIN avaliacao av ON a.id_atendimento = av.id_atendimento
        GROUP BY at.nome;
    """)
    dados_atendentes = cursor.fetchall()
    cursor.close()
    conn.close()

    prompt = f"""
    Você é um consultor operacional de um Sistema de Gestão de Filas Inteligente (SGFI).
    Analise os indicadores reais extraídos do banco de dados MySQL agora:
    - Tempo médio de espera por unidade (minutos): {dados_espera}
    - Desempenho dos atendentes (nome, total atendimentos, nota média de 1 a 5): {dados_atendentes}
    
    Gere um diagnóstico executivo curto (3 tópicos) recomendando realocação de atendentes ou ajustes nas filas para reduzir o tempo de espera e melhorar a satisfação.
    """

    print("\nConsultando IA Generativa (Gemini) com os dados do banco...")
    client = genai.Client(
        api_key=api_key,
        http_options={"api_version": "v1beta"}
    )
    modelos = [
        "gemini-3.1-flash-lite-preview",
        "gemini-3-flash-preview",
        "gemini-3.1-pro-preview"
    ]
    resposta_texto = None
    ultimo_erro = None

    for m in modelos:
        try:
            response = client.models.generate_content(model=m, contents=prompt)
            resposta_texto = response.text
            break
        except Exception as e:
            ultimo_erro = e
            continue

    if resposta_texto:
        print("\n=== RECOMENDAÇÕES DA IA GENERATIVA (TOMADA DE DECISÃO) ===")
        print(resposta_texto)
    else:
        print(f"[ERRO DETALHADO]: {ultimo_erro}")


