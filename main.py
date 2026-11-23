from ddl_dml import criar_e_popular_banco, eliminar_todas_tabelas
from crud import menu_crud
from relatorios_graficos import executar_consulta_e_grafico
from ia_assistente import analisar_operacao_com_ia

def main():
    while True:
        print("\n====================================================")
        print("  SGFI - SISTEMA DE GESTÃO DE FILAS INTELIGENTE")
        print("====================================================")
        print("1. Criar banco/tabelas e carregar dados iniciais (DDL + DML)")
        print("2. Eliminar todas as tabelas do banco (DROP TABLES)")
        print("3. Gerenciar Tabelas - CRUD (Inserir/Atualizar/Excluir/Consultar)")
        print("4. Executar Consultas Analíticas (Tabela + Gráfico)")
        print("5. Assistente Inteligente (Análise Operacional com IA Generativa)")
        print("0. Sair")
        opcao = input("Escolha uma opção: ").strip()

        try:
            if opcao == "1":
                criar_e_popular_banco()
            elif opcao == "2":
                confirm = input("Tem certeza que deseja apagar TODAS as tabelas? (s/n): ")
                if confirm.lower() == "s":
                    eliminar_todas_tabelas()
            elif opcao == "3":
                menu_crud()
            elif opcao == "4":
                executar_consulta_e_grafico()
            elif opcao == "5":
                analisar_operacao_com_ia()
            elif opcao == "0":
                print("Encerrando o sistema...")
                break
            else:
                print("Opção inválida!")
        except Exception as e:
            print(f"[ERRO]: {e}")

if __name__ == "__main__":
    main()