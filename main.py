import pandas as pd
import numpy as np
import scipy.stats as stats

#Professor, eu faço meus comentários em inglês mesmo, não estranhe

df = pd.read_csv("dataset_delivery_fraude_avaliacoes.csv")

# Methods

def mediana_ponderada(dados, pesos):
    #The * unzip the list and create separated args (dados, pesos)
    dados_ordenados, pesos_ordenados = zip(*sorted(zip(dados, pesos)))
    soma_pesos = np.cumsum(pesos_ordenados)
    # this will return dados_ordenados[result]
    return dados_ordenados[np.searchsorted(soma_pesos, soma_pesos[-1] / 2)]

def media_ponderada(dados, pesos):
    dados_arr = np.array(dados)
    pesos_arr = np.array(pesos)

    soma_produtos = np.sum(dados_arr * pesos_arr)
    soma_pesos = np.sum(pesos_arr)

    return soma_produtos / soma_pesos

def calcular_iqr(dados):
    q1, q3 = np.percentile(dados, [25, 75])
    iqr = q3 - q1
    return iqr

def calcular_limite_inferior_usando_iqr(dados):
    q1, q3 = np.percentile(dados, [25, 75])
    iqr = q3 - q1

    limite_inferior = q1 - (iqr * 1.5)
    return limite_inferior

def calcular_limite_superior_usando_iqr(dados):
    q1, q3 = np.percentile(dados, [25, 75])
    iqr = q3 - q1

    limite_superior = q3 + (iqr * 1.5)
    return limite_superior

def classificar_coluna(dado, p25, p75):
    if dado > p75:
        return "Alta"
    elif dado < p25:
        return "Baixa"
    else:
        return "Média"

#Phase 1 - A média mente para você?
media_preco = df["preco_pedido"].mean()
mediana_preco = np.average(df["preco_pedido"])
media_aparada_preco = stats.trim_mean(df["preco_pedido"], proportiontocut=0.1)

print(mediana_preco, media_preco, media_aparada_preco)

'''
Perguntas: 
    1 - Não existe diferença entre a media e a mediana, mas temos diferença entre esses dois e a média aparada
    2 - Já que temos diferença entre a media e a media aparada, há sim evidências de outliers 
    3 - Eu usaria a mediana, pois a media não se deixa afetar pelos outliers. (Não sabemos se 10% é suficiente para limpar a média)
'''

#Phase 2 - Peso muda a realidade
media_ponderada_nota = media_ponderada(df["nota_cliente"], df["preco_pedido"])
media_nota = np.mean(df["nota_cliente"])
print(media_ponderada_nota, media_nota)

'''
Perguntas:
    1 - Restaurantes caros não parecem melhor, pois a media ponderada e a media normal não tem muita diferença.
    2 - Isso é viés, estamos usando todos os registros dentro do dataframe, inclusive os outliers de nota e preço
'''

#Phase 3 - Caçando outliers
iqr_tempo_entrega = calcular_iqr(df["tempo_entrega_min"])
limite_inferior_tempo_entrega = calcular_limite_inferior_usando_iqr(df["tempo_entrega_min"])
limite_superior_tempo_entrega = calcular_limite_superior_usando_iqr(df["tempo_entrega_min"])
outliers_tempo_entrega = [x for x in df["tempo_entrega_min"] if x < limite_inferior_tempo_entrega or x > limite_superior_tempo_entrega]
media_tempo_entrega = np.mean(df["tempo_entrega_min"])
media_aparada_tempo_entrega = stats.trim_mean(df["tempo_entrega_min"], proportiontocut=0.15)
print(media_tempo_entrega, media_aparada_tempo_entrega, limite_inferior_tempo_entrega, limite_superior_tempo_entrega, np.sort(outliers_tempo_entrega))

'''
Perguntas:
    1 - Existem 14 outliers
    2 - Não, pois mesmo retirando os outliers, a media continua bem parecida
    3 - Eu não removeria esses pontos. Já que os outliers não tem um impacto grande na média, não tem motivo para tirar
'''

#Phase 4
p25, p50, p75, p90 = np.percentile(df["preco_pedido"], [25, 50, 75, 90])
mediana_ponderada_preco = mediana_ponderada(df["preco_pedido"], df['qtd_itens'])
print(p25, p50, p75, p90, mediana_ponderada_preco)

'''
Perguntas:
    1 - Depois de descobrir o valor do percentil 90 e da mediana ponderada usando a quantidade de itens como peso.
    Podemos dizer que o que define um pedido caro de verdade é tudo que está acima do percentil 90 (+= 160.7)
'''

#Phase 5
taxa_entrega_p25, taxa_entrega_p75 = np.percentile(df["taxa_entrega"], [25, 75])

# the function apply goes through every register of a column and apply any function inside the parentheses
df["classe_taxa"] = df["taxa_entrega"].apply(lambda x: classificar_coluna(x, taxa_entrega_p25, taxa_entrega_p75))

#crosstab function cross two different columns and add one "point" to each class (alta, baixa, media)
tabela_probabilidade_categoria = pd.crosstab(
    df["categoria"],
    df["classe_taxa"],
    normalize='index' #this is to display as percentage (0.n)
)

#for better visualization
#tabela_probabilidade_categoria = tabela_probabilidade_categoria * 100
print(tabela_probabilidade_categoria.round(1))

media_taxa_por_categoria = df.groupby('categoria')['taxa_entrega'].mean()
print(media_taxa_por_categoria.round(2))

tabela_retornos = pd.DataFrame()

tabela_retornos['Retorno_Alta'] = media_taxa_por_categoria * 1.5
tabela_retornos['Retorno_Media'] = media_taxa_por_categoria * 1.0
tabela_retornos['Retorno_Baixa'] = media_taxa_por_categoria * 0.5
print(tabela_retornos.round(2))


ev_alta = tabela_probabilidade_categoria['Alta'] * tabela_retornos['Retorno_Alta']
ev_media = tabela_probabilidade_categoria['Média'] * tabela_retornos['Retorno_Media']
ev_baixa = tabela_probabilidade_categoria['Baixa'] * tabela_retornos['Retorno_Baixa']

ev_final = ev_alta + ev_media + ev_baixa

resultado_ev = pd.DataFrame({
    'Média antiga': media_taxa_por_categoria,
    "EV": ev_final
})
print(resultado_ev.round(2))

'''
Perguntas:
    1 - O maior EV é do Café
    2 - Sim, podemos ver que o café tem um EV muito maior que a média antiga comparando com as outras categorias. Mas ainda não temos certeza
'''