import pandas as pd
import numpy as np
import scipy.stats as stats

df = pd.read_csv("dataset_delivery_fraude_avaliacoes.csv")

#Phase 1 - A média mente para você?
media_preco = df["preco_pedido"].mean()
mediana_preco = np.average(df["preco_pedido"])
media_aparada_preco = stats.trim_mean(df["preco_pedido"], proportiontocut=0.1)

'''
Perguntas: 
    1 - Não existe diferença entre a media e a mediana, mas temos diferença entre esses dois e a média aparada
    2 - Já que temos diferença entre a media e a media aparada, há sim evidências de outliers 
    3 - Eu usaria a mediana, pois não sabemos se 10% é o suficiente para pegar todos os outliers
'''
print(mediana_preco, media_preco, media_aparada_preco)

#Phase 2 - Peso muda a realidade

media_ponderada_nota_preco = np.average(df["nota_cliente"], weights=df["preco_pedido"])
print(media_ponderada_nota_preco)
