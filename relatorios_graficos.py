import matplotlib.pyplot as plt
from conexao import conectar

CONSULTAS = {
    "1": {
        "titulo": "Total de Atendimentos Concluídos por Serviço",
        "xlabel": "Serviço",
        "ylabel": "Total de Atendimentos",
        "sql": """
            SELECT s.nome_servic AS servico, COUNT(a.id_atendimento) AS total_atendimentos
            FROM servico s
            INNER JOIN servico_fila sf ON s.id_servico = sf.id_servico
            INNER JOIN fila f ON sf.id_fila = f.id_fila
            INNER JOIN entra_fila ef ON f.id_fila = ef.id_fila
            INNER JOIN atendimento a ON ef.id_entrad_fila = a.id_entrad_fila
            WHERE a.status_atendimento = 'CONCLUIDO'
            GROUP BY s.id_servico, s.nome_servic
            ORDER BY total_atendimentos DESC;
        """
    },
    "2": {
        "titulo": "Tempo Médio de Espera nas Filas por Unidade (min)",
        "xlabel": "Unidade",
        "ylabel": "Tempo Médio (min)",
        "sql": """
            SELECT u.nome_unid AS unidade,
                   ROUND(AVG(TIMESTAMPDIFF(MINUTE, ef.data_hr_entrad, a.hr_inicio)), 1) AS tempo_medio_espera_min
            FROM unidade u
            INNER JOIN unidade_servico us ON u.id_unidade = us.id_unidade
            INNER JOIN servico_fila sf ON us.id_servico = sf.id_servico
            INNER JOIN entra_fila ef ON sf.id_fila = ef.id_fila
            INNER JOIN atendimento a ON ef.id_entrad_fila = a.id_entrad_fila
            GROUP BY u.id_unidade, u.nome_unid
            ORDER BY tempo_medio_espera_min DESC;
        """
    },
    "3": {
        "titulo": "Produtividade por Atendente (Atendimentos Concluídos)",
        "xlabel": "Atendente",
        "ylabel": "Atendimentos Concluídos",
        "sql": """
            SELECT at.nome AS atendente, COUNT(a.id_atendimento) AS atendimentos_concluidos,
                   ROUND(AVG(av.nota), 2) AS media_avaliacao
            FROM atendente at
            INNER JOIN atendimento a ON at.id_atendente = a.id_atendente
            LEFT JOIN avaliacao av ON a.id_atendimento = av.id_atendimento
            WHERE a.status_atendimento = 'CONCLUIDO'
            GROUP BY at.id_atendente, at.nome
            ORDER BY atendimentos_concluidos DESC;
        """
    }
}

def executar_consulta_e_grafico():
    print("\n=== CONSULTAS ANALÍTICAS (ITEM 6) ===")
    print("1. Total de atendimentos concluídos por Serviço")
    print("2. Tempo médio de espera nas filas por Unidade")
    print("3. Produtividade e média de avaliação por Atendente")
    escolha = input("Escolha a consulta (1-3): ").strip()

    if escolha not in CONSULTAS:
        return

    item = CONSULTAS[escolha]
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(item["sql"])
    colunas = [desc[0] for desc in cursor.description]
    linhas = cursor.fetchall()
    cursor.close()
    conn.close()

    # Exibição Tabular
    print(f"\n--- {item['titulo']} ---")
    print(" | ".join(f"{c:<28}" for c in colunas))
    print("-" * (30 * len(colunas)))
    for l in linhas:
        print(" | ".join(f"{str(v):<28}" for v in l))

    # Exibição Gráfica (usando as 2 primeiras colunas para X e Y)
    if linhas:
        eixo_x = [str(l[0]) for l in linhas]
        eixo_y = [float(l[1]) for l in linhas]
        plt.figure(figsize=(8, 5))
        plt.bar(eixo_x, eixo_y, color="#1b4f72")
        plt.title(item["titulo"])
        plt.xlabel(item["xlabel"])
        plt.ylabel(item["ylabel"])
        plt.tight_layout()
        plt.show()