import pandas as pd
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator
from pgmpy.inference import VariableElimination

# === 1. LEITURA DO CSV ===
dados = pd.read_csv('alerts_novo.csv')
dados.columns = dados.columns.str.strip().str.lower()

# === 2. DISCRETIZAÇÃO ===
def discretizar_alertas(df):
    df_disc = df.copy()

    # Temperatura (°C)
    df_disc['temp_cat'] = pd.cut(
        df_disc['temp'],
        bins=[0, 17, 27, 54],
        labels=['baixa', 'moderada', 'alta']
    )

    # Humidade (%)
    df_disc['hum_cat'] = pd.cut(
        df_disc['hum'],
        bins=[0, 34, 55, 79],
        labels=['baixa', 'moderada', 'alta']
    )

    # Velocidade do vento (km/h)
    df_disc['wind_cat'] = pd.cut(
        df_disc['wind'],
        bins=[0, 10, 20, 32],
        labels=['baixa', 'moderada', 'alta',]
    )

    # Risco de incêndio
    df_disc['risco_cat'] = df_disc['risco_incendio'].astype(str).map({
        'baixo': 'baixo',
        'moderado': 'moderado',
        'alto': 'alto'
    })

    return df_disc


df_disc = discretizar_alertas(dados)

# === 3. PREPARAÇÃO DO DATASET PARA TREINO ===
# Garante que todas as colunas estão lá
for col in ['temp_cat', 'hum_cat', 'wind_cat', 'risco_cat']:
    if col not in df_disc.columns:
        raise ValueError(f"Coluna em falta: {col}")

# Remove apenas linhas completamente nulas
df_treino = df_disc[['temp_cat', 'hum_cat', 'wind_cat', 'risco_cat']].dropna(how='any').copy()
for col in df_treino.columns:
    df_treino[col] = df_treino[col].astype(str)

# === 4. ESTRUTURA DA REDE BAYESIANA ===
modelo = DiscreteBayesianNetwork([
    ('temp_cat', 'risco_cat'),
    ('hum_cat', 'risco_cat'),
    ('wind_cat', 'risco_cat')
])

modelo.fit(df_treino, estimator=MaximumLikelihoodEstimator)

# === 5. INFERÊNCIA ===
inferencia = VariableElimination(modelo)

print("\n================ REDE BAYESIANA DE RISCO DE INCÊNDIO ================\n")
print("Nós:", modelo.nodes())
print("\nArestas:")
for edge in modelo.edges():
    print(f"  {edge[0]} -> {edge[1]}")

print("\n[1] P(Risco | Temp = alta)")
resultado = inferencia.query(variables=['risco_cat'], evidence={'temp_cat': 'alta'})
print(resultado)

print(df_disc['risco_cat'].value_counts())
