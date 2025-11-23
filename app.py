from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

app = Flask(__name__)
ARQUIVO = "controle_financeiro.csv"
COLUNAS = ["data", "tipo", "categoria", "valor"]


def ler_dados():
    if not os.path.exists(ARQUIVO):
        df = pd.DataFrame(columns=COLUNAS)
        df.to_csv(ARQUIVO, index=False)
        return df
    return pd.read_csv(ARQUIVO)


def salvar_dados(df):
    df.to_csv(ARQUIVO, index=False)


def gerar_grafico(df):
    if df.empty:
        return None

    gastos_cat = df[df['tipo'] == 'Despesa'].groupby('categoria')['valor'].sum()
    balanco = df.groupby('tipo')['valor'].sum()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    fig.patch.set_facecolor('#f8f9fa')

    if not gastos_cat.empty:
        ax1.bar(gastos_cat.index, gastos_cat.values, color='#ff6b6b')
        ax1.set_title('Despesas por Categoria')
        ax1.tick_params(axis='x', rotation=45)

    if not balanco.empty:
        cores = ['#ff6b6b', '#1dd1a1'] if 'Despesa' in balanco else ['#1dd1a1']
        ax2.pie(balanco, labels=balanco.index, autopct='%1.1f%%', colors=cores, startangle=90)
        ax2.set_title('Receitas vs Despesas')

    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url


@app.route('/')
def index():
    df = ler_dados()

    total_receita = df[df['tipo'] == 'Receita']['valor'].sum() if not df.empty else 0
    total_despesa = df[df['tipo'] == 'Despesa']['valor'].sum() if not df.empty else 0
    saldo = total_receita - total_despesa

    grafico = gerar_grafico(df)

    transacoes = df.to_dict(orient='records')
    for i, t in enumerate(transacoes):
        t['id'] = i

    transacoes = transacoes[::-1]

    return render_template('index.html',
                           transacoes=transacoes,
                           saldo=saldo,
                           receita=total_receita,
                           despesa=total_despesa,
                           grafico=grafico)


@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        categoria = request.form.get('categoria')
        valor = float(request.form.get('valor'))
        data = request.form.get('data')

        if not data:
            data = datetime.now().strftime("%Y-%m-%d")

        nova_linha = {
            "data": [data],
            "tipo": [tipo],
            "categoria": [categoria],
            "valor": [valor]
        }

        df = ler_dados()
        df = pd.concat([df, pd.DataFrame(nova_linha)], ignore_index=True)
        salvar_dados(df)

        return redirect(url_for('index'))

    return render_template('adicionar.html')


@app.route('/deletar/<int:id>')
def deletar(id):
    df = ler_dados()
    if id in df.index:
        df = df.drop(id)
        salvar_dados(df)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)