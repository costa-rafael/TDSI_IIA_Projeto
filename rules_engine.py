import pandas as pd

dados = pd.read_csv("alerts.csv")
dados.columns = dados.columns.str.strip().str.lower()

def avaliar_regras(linha):
    temp = linha['temp']
    hum = linha['hum']
    wind = linha['wind']
    event = str(linha['event_type']).title()

    regras_ativas = []

    # ============================================================
    #  REGRAS BASEADAS EM TEMPERATURA, HUMIDADE E VENTO
    # ============================================================
    if temp >= 30:
        if hum <= 25:
            if wind >= 20:
                regras_ativas.append(('alto', 'Calor extremo e vento intenso: ativar alerta máximo; notificar Proteção Civil e encerrar acessos públicos.'))
            else:
                regras_ativas.append(('alto', 'Temperatura muito alta: emitir aviso laranja e intensificar monitorização.'))
        elif hum <= 50:
            if wind >= 20:
                regras_ativas.append(('alto', 'Calor elevado, humidade baixa e vento intenso: risco severo; mobilizar equipas de vigilância.'))
            else:
                regras_ativas.append(('moderado', 'Calor forte mas humidade estabilizadora: observar condições sem necessidade de intervenção.'))
        else: # hum > 50
            if wind >= 20:
                regras_ativas.append(('moderado', 'Vento intenso com humidade alta: emitir aviso laranja e manter atenção.'))
            else:
                regras_ativas.append(('moderado', 'Calor elevado mas humidade alta: manter vigilância normal.'))

    elif 20 <= temp < 30:
        if hum <= 25:
            if wind >= 20:
                regras_ativas.append(('alto', 'Ar muito seco e vento forte: emitir aviso vermelho e reforçar controlo de ignições.'))
            else:
                regras_ativas.append(('moderado', 'Calor seco com vento fraco: manter monitorização ativa.'))
        elif hum <= 50:
            if wind >= 20:
                regras_ativas.append(('moderado', 'Vento forte com humidade média: aviso laranja e reforço de observação.'))
            else:
                regras_ativas.append(('baixo', 'Condições estáveis: risco controlado, vigilância de rotina suficiente.'))
        else: # hum > 50
            regras_ativas.append(('baixo', 'Condições seguras: calor moderado e humidade adequada.'))

    else:  # temp < 20
        if hum <= 25:
            if wind >= 20:
                regras_ativas.append(('moderado', 'Vento muito forte em ar seco: atenção reforçada, possíveis ignições.'))
            else:
                regras_ativas.append(('baixo', 'Ar seco mas temperaturas baixas: manter observação de rotina.'))
        else: # hum > 25
            regras_ativas.append(('baixo', 'Condições seguras: risco de incêndio mínimo.'))

    # ============================================================
    #  EVENTOS (mantêm risco baixo para compatibilidade bayesiana)
    # ============================================================
    if event == 'Smoke':
        regras_ativas.append(('baixo', 'Deteção de fumo: enviar equipa de verificação imediata.'))
    if event == 'Heat' and temp >= 35:
        regras_ativas.append(('baixo', 'Evento de calor: reforçar comunicação pública e alertar serviços.'))
    if event == 'Noise':
        regras_ativas.append(('baixo', 'Ruído anómalo: acionar manutenção preventiva.'))
    if wind >= 80:
        regras_ativas.append(('baixo', 'Rajadas superiores a 80 km/h: emitir aviso meteorológico e restringir acessos.'))
    if temp <= 5:
        regras_ativas.append(('baixo', 'Temperaturas muito baixas: monitorizar condições e garantir segurança operacional.'))

    # ============================================================
    #  CÁLCULO FINAL DO RISCO E AGREGAÇÃO DE AÇÕES
    # ============================================================
    prioridade = {'baixo': 1, 'moderado': 2, 'alto': 3}

    # Loop pelas regras ativas para determinar o risco final e ações
    if regras_ativas:
        maior_prioridade = -1
        risco_final = 'baixo'
        acoes = []

        for item in regras_ativas:
            if not isinstance(item, tuple) or len(item) != 2:
                continue
            r, a = item
            if prioridade.get(r, 0) > maior_prioridade:
                maior_prioridade = prioridade[r]
                risco_final = r
            acoes.append(a)

        # Remove duplicados mantendo ordem
        acoes_unicas = []
        for acao in acoes:
            if acao not in acoes_unicas:
                acoes_unicas.append(acao)

    else:
        risco_final = 'baixo'
        acoes_unicas = ['Classificação automática: manter vigilância mínima e registo do evento.']

    return risco_final, acoes_unicas


def processar_csv():
    riscos = []
    print("\n================ SISTEMA DE AVALIAÇÃO DE RISCO DE INCÊNDIO ================\n")

    for _, linha in dados.iterrows():
        risco, acoes = avaliar_regras(linha)
        riscos.append(risco)

        temp = linha['temp']
        hum = linha['hum']
        wind = linha['wind']
        zona = linha['zone']
        evento = linha['event_type']
        timestamp = linha['timestamp']

        # Construção visual do alerta
        print("┌" + "─" * 70 + "┐")
        print(f" Data/Hora: {timestamp} │ Zona: {zona} │ Evento: {evento}")
        print(f" Temperatura: {temp:^5.1f}°C │ Humidade: {hum:^5.1f}% │ Vento: {wind:^5.1f}km/h")
        print("├" + "─" * 70 + "┤")
        print(f" ⚠ Nível de Risco: {risco.upper()}")
        print(f" 🔹 Ações Recomendadas:")
        for acao in acoes:
            print(f"   - {acao:<65}")
        print("└" + "─" * 70 + "┘\n")

    dados['risco_incendio'] = riscos
    dados.to_csv('alerts_novo.csv', index=False)
    print('\n✓ Ficheiro alerts_novo.csv criado com coluna de risco_incendio.\n')


processar_csv()

print(dados.hum.min()) 
print(dados.hum.max())
print(dados.temp.min())
print(dados.temp.max())
print(dados.wind.min())
print(dados.wind.max())
