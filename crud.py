from conexao import conectar

TABELAS = [
    "estabelecimento", "unidade", "horar_funcionamento", "administrador",
    "configuracao", "relatorio", "servico", "fila", "unidade_servico",
    "servico_fila", "cliente", "atendente", "guiche", "notificacao",
    "entra_fila", "atendimento", "avaliacao"
]

def menu_crud():
    print("\n=== SELECIONE A TABELA PARA OPERAR (CRUD) ===")
    for i, t in enumerate(TABELAS, 1):
        print(f"{i:2d}. {t}")
    print(" 0. Voltar")
    
    try:
        op = int(input("Escolha o número da tabela: "))
        if op == 0 or op < 1 or op > len(TABELAS):
            return
    except ValueError:
        return

    tabela = TABELAS[op - 1]
    while True:
        print(f"\n--- CRUD: {tabela.upper()} ---")
        print("1. Consultar (SELECT)")
        print("2. Inserir (INSERT)")
        print("3. Atualizar (UPDATE)")
        print("4. Excluir (DELETE)")
        print("0. Voltar")
        acao = input("Opção: ")

        conn = conectar()
        cursor = conn.cursor()
        try:
            # Descobre colunas, PKs e colunas geradas automaticamente
            cursor.execute(f"SHOW COLUMNS FROM {tabela};")
            colunas_info = cursor.fetchall()
            # col[0]=Field, col[3]=Key ('PRI'), col[5]=Extra ('auto_increment' ou 'STORED GENERATED')
            todas_cols = [c[0] for c in colunas_info if "GENERATED" not in c[5]]
            pks = [c[0] for c in colunas_info if c[3] == "PRI"]
            editaveis = [c[0] for c in colunas_info if "auto_increment" not in c[5] and "GENERATED" not in c[5]]

            if acao == "1":
                cursor.execute(f"SELECT {', '.join(todas_cols)} FROM {tabela};")
                rows = cursor.fetchall()
                print(f"\nColunas: {todas_cols}")
                for r in rows:
                    print(r)
                if not rows:
                    print("(Nenhum registro encontrado)")

            elif acao == "2":
                print(f"Campos para preencher (deixe vazio para NULL/DEFAULT): {editaveis}")
                cols_insert, vals_insert = [], []
                for col in editaveis:
                    val = input(f"  {col}: ").strip()
                    if val != "":
                        cols_insert.append(col)
                        vals_insert.append(val)
                placeholders = ", ".join(["%s"] * len(vals_insert))
                sql = f"INSERT INTO {tabela} ({', '.join(cols_insert)}) VALUES ({placeholders});"
                cursor.execute(sql, vals_insert)
                conn.commit()
                print("[OK] Registro inserido com sucesso!")

            elif acao == "3":
                where_clauses, where_vals = [], []
                print(f"Informe a Chave Primária {pks} do registro a atualizar:")
                for pk in pks:
                    where_clauses.append(f"{pk} = %s")
                    where_vals.append(input(f"  {pk}: ").strip())
                print(f"Colunas disponíveis para alteração: {editaveis}")
                col_alvo = input("Qual coluna deseja alterar? ").strip()
                novo_val = input(f"Novo valor para {col_alvo}: ").strip()
                sql = f"UPDATE {tabela} SET {col_alvo} = %s WHERE {' AND '.join(where_clauses)};"
                cursor.execute(sql, [novo_val] + where_vals)
                conn.commit()
                print(f"[OK] {cursor.rowcount} registro(s) atualizado(s)!")

            elif acao == "4":
                where_clauses, where_vals = [], []
                print(f"Informe a Chave Primária {pks} do registro a excluir:")
                for pk in pks:
                    where_clauses.append(f"{pk} = %s")
                    where_vals.append(input(f"  {pk}: ").strip())
                sql = f"DELETE FROM {tabela} WHERE {' AND '.join(where_clauses)};"
                cursor.execute(sql, where_vals)
                conn.commit()
                print(f"[OK] {cursor.rowcount} registro(s) excluído(s)!")

            elif acao == "0":
                break
        except Exception as e:
            print(f"[ERRO DE INTEGRIDADE / SQL]: {e}")
        finally:
            cursor.close()
            conn.close()