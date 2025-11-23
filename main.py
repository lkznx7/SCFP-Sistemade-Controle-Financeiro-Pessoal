import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

class Financeiro:
    def __init__(self, nome_arquivo="ControleFinanceiro.csv"):
        self.arquivo = nome_arquivo
        self.colunas = ["data", "tipo", "categoria", "valor"]

        if not os.path.exists(self.arquivo):
            self._criar_novo_csv()
        else:
            try:
                df = pd.read_csv(self.arquivo)
                if "tipo" not in df.columns:
                    print("⚠!!Arquivo antigo detectado! Atualizando estrutura do banco de dados...")
                    self._criar_novo_csv()
            except Exception:
                self._criar_novo_csv()

    def _criar_novo_csv(self):
        df = pd.DataFrame(columns=self.colunas)
        df.to_csv(self.arquivo, index=False)
        print(f"Arquivo '{self.arquivo}' configurado com sucesso.")

    def _salvar(self, df):
        df.to_csv(self.arquivo, index=False)

    def _ler(self):
        return pd.read_csv(self.arquivo)

    def adicionar_receita(self):
        try:
            valor = float(input("Valor da Receita: R$ "))
            cat = input("Fonte (ex: Salário, Venda): ")
            data_input = input("Data (AAAA-MM-DD) ou [Enter] para hoje: ")

            if data_input == "":
                data_input = datetime.now().strftime("%Y-%m-%d")

            nova_linha = {
                "data": [data_input],
                "tipo": ["Receita"],
                "categoria": [cat],
                "valor": [valor]
            }

            df = self._ler()
            df = pd.concat([df, pd.DataFrame(nova_linha)], ignore_index=True)
            self._salvar(df)
            print("Receita adicionada!")
        except ValueError:
            print("Erro: Digite um valor numérico válido.")

    def adicionar_despesa(self):
        try:
            valor = float(input("Valor da Despesa: R$ "))
            cat = input("Categoria (ex: Mercado, Luz): ")
            data_input = input("Data (AAAA-MM-DD) ou [Enter] para hoje: ")

            if data_input == "":
                data_input = datetime.now().strftime("%Y-%m-%d")

            nova_linha = {
                "data": [data_input],
                "tipo": ["Despesa"],
                "categoria": [cat],
                "valor": [valor]
            }

            df = self._ler()
            df = pd.concat([df, pd.DataFrame(nova_linha)], ignore_index=True)
            self._salvar(df)
            print("Despesa adicionada!")
        except ValueError:
            print("Erro: Digite um valor numérico válido.")

    def listar_despesas(self):
        df = self._ler()
        if df.empty:
            print("Nenhum dado cadastrado.")
            return

        despesas = df[df["tipo"] == "Despesa"]
        if despesas.empty:
            print("Nenhuma despesa cadastrada.")
        else:
            print("\n--- Lista de Despesas ---")
            print(despesas)

    def editar_despesa(self):
        df = self._ler()
        if df.empty:
            print("Nada para editar.")
            return

        print(df)

        try:
            idx = int(input("Índice para editar: "))
            if idx in df.index:
                coluna = input("Coluna (data, categoria, valor): ").lower()
                if coluna in df.columns:
                    novo_valor = input(f"Novo valor: ")
                    df.at[idx, coluna] = novo_valor
                    self._salvar(df)
                    print("Editado com sucesso!")
                else:
                    print("Coluna inválida.")
            else:
                print("Índice não encontrado.")
        except ValueError:
            print("Erro de valor.")

    def remover_despesa(self):
        df = self._ler()
        if df.empty:
            print("Nada para remover.")
            return

        print(df)
        try:
            idx = int(input("Índice para EXCLUIR: "))
            if idx in df.index:
                df = df.drop(idx)
                self._salvar(df)
                print("Removido com sucesso.")
            else:
                print("Índice inválido.")
        except ValueError:
            print("Erro de digitação.")

    def calcular_saldo(self):
        df = self._ler()
        if df.empty:
            print("Sem dados para calcular saldo.")
            return 0

        total_receitas = df[df["tipo"] == "Receita"]["valor"].sum()
        total_despesas = df[df["tipo"] == "Despesa"]["valor"].sum()
        saldo = total_receitas - total_despesas
        print(f"\nReceitas: R$ {total_receitas:.2f}")
        print(f"Despesas: R$ {total_despesas:.2f}")
        print(f"SALDO: R$ {saldo:.2f}")
        return saldo

    def despesas_por_categoria(self):
        df = self._ler()
        if df.empty: return

        df_desp = df[df["tipo"] == "Despesa"]
        if not df_desp.empty:
            print("\n--- Por Categoria ---")
            print(df_desp.groupby("categoria")["valor"].sum())

    def gastos_por_mes(self):
        df = self._ler()
        if df.empty: return

        try:
            df["data"] = pd.to_datetime(df["data"])
            df["mes"] = df["data"].dt.to_period("M")
            df_desp = df[df["tipo"] == "Despesa"]
            if not df_desp.empty:
                print("\n--- Por Mês ---")
                print(df_desp.groupby("mes")["valor"].sum())
        except Exception as e:
            print(f"Erro ao processar datas: {e}")

    def receita_vs_despesa_mensal(self):
        df = self._ler()
        if df.empty: return

        try:
            df["data"] = pd.to_datetime(df["data"])
            df["mes"] = df["data"].dt.to_period("M")
            relatorio = df.groupby(["mes", "tipo"])["valor"].sum().unstack()
            print("\n--- Comparativo Mensal ---")
            print(relatorio.fillna(0))
        except Exception as e:
            print(f"Erro ao gerar relatório mensal: {e}")

    def pegar_dados_para_exportar(self):
        df = self._ler()
        return df.to_dict(orient="records")

    def gerar_dashboard(self):
        df = self._ler()

        if df.empty:
            print("Sem dados para gerar gráficos.")
            return

        df_desp = df[df["tipo"] == "Despesa"]
        if df_desp.empty:
            print("Sem despesas para exibir no gráfico.")
            return

        dados_categoria = df_desp.groupby("categoria")["valor"].sum()
        dados_gerais = df.groupby("tipo")["valor"].sum()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        ax1.bar(dados_categoria.index, dados_categoria.values, color='salmon')
        ax1.set_title('Despesas por Categoria')
        ax1.set_ylabel('Valor (R$)')
        ax1.tick_params(axis='x', rotation=45)

        cores = ['#ff9999', '#66b3ff']
        ax2.pie(dados_gerais, labels=dados_gerais.index, autopct='%1.1f%%', colors=cores, startangle=90)
        ax2.set_title('Balanço Geral')

        plt.tight_layout()

        print("Abrindo janela de gráficos...")
        plt.show()

sistema = Financeiro()

while True:
    print("\n1. Adicionar Receita")
    print("2. Adicionar Despesa")
    print("3. Listar/Editar/Remover")
    print("4. Relatórios e Saldo")
    print("5. Gerar Gráficos Visuais")
    print("6. Sair")

    opcao = input("Escolha: ")

    if opcao == "1":
        sistema.adicionar_receita()
    elif opcao == "2":
        sistema.adicionar_despesa()
    elif opcao == "3":
        sub = input("[L]istar, [E]ditar, [R]emover: ").upper()
        if sub == "L":
            sistema.listar_despesas()
        elif sub == "E":
            sistema.editar_despesa()
        elif sub == "R":
            sistema.remover_despesa()
        else:
            print("Opção inválida!")

    elif opcao == "4":
        sistema.calcular_saldo()
        print("-" * 20)
        sistema.receita_vs_despesa_mensal()

    elif opcao == "5":
        sistema.gerar_dashboard()

    elif opcao == "6":
        print("Saindo do sistema...")
        break
    else:
        print("Opção inválida.")