from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.config import settings

llm = ChatOpenAI(model=settings.openai_model, temperature=0.1)

resumo_prontuario_prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um médico intensivista especializado em sumarização de prontuários. "
     "Gere um resumo clínico conciso e identifique alertas críticos."),
    ("human", "Paciente: {nome}, {idade} anos\nDiagnósticos: {diagnosticos}\n"
     "Alergias: {alergias}\nExames: {exames}\nEvolução: {evolucao}"),
])

sumarizacao_evolucao_prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um médico intensivista. Sumarize a evolução clínica dos últimos {dias} dias. "
     "Identifique: resumo do período, principais intercorrências, tendência clínica "
     "(MELHORA/ESTAVEL/PIORA), condutas realizadas, próximos passos e risco atual."),
    ("human", "{evolucao}"),
])

insights_dashboard_prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um analista de dados hospitalares. Analise os KPIs e gere:\n"
     "1. Resumo executivo\n2. Insights com situação e ação sugerida para cada indicador\n"
     "3. Prioridade de intervenção (ordenada por criticidade)"),
    ("human", "{kpis}"),
])

assistente_documentacao_prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um médico especialista em documentação clínica. Com base no contexto clínico "
     "e no texto ditado pelo médico, retorne APENAS um JSON válido (sem markdown, sem ```) "
     "com esta estrutura exata:\n"
     '{{\n'
     '  "texto_evolucao_sugerido": "texto completo da evolução",\n'
     '  "qualidade_estimada": "ALTA" ou "MEDIA" ou "BAIXA",\n'
     '  "evolucao_estruturada": {{\n'
     '    "subjetivo": "queixas do paciente",\n'
     '    "objetivo": "achados do exame físico",\n'
     '    "avaliacao": "análise clínica",\n'
     '    "plano": "conduta e prescrições"\n'
     '  }},\n'
     '  "campos_preenchidos": ["campo1", "campo2"],\n'
     '  "campos_faltantes": ["campo1", "campo2"],\n'
     '  "cids_sugeridos": ["CID1", "CID2"],\n'
     '  "alertas_documentacao": ["alerta1", "alerta2"]\n'
     "}}"),
    ("human", "Contexto clínico: {contexto}\n\nTexto do médico: {texto_clinico}"),
])

copilot_regulatorio_prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um especialista em regulação médica. "
     "Com base na descrição do caso, retorne APENAS um JSON válido (sem markdown, sem ```) "
     "com esta estrutura exata:\n"
     '{{\n'
     '  "justificativa_clinica": "texto completo da justificativa",\n'
     '  "argumentos_principais": ["arg1", "arg2", ...],\n'
     '  "embasamento_cientifico": ["ref1", "ref2", ...],\n'
     '  "documentos_necessarios": ["doc1", "doc2", ...],\n'
     '  "pontos_atencao": ["ponto1", "ponto2", ...],\n'
     '  "probabilidade_aprovacao": 85\n'
     "}}"),
    ("human", "Descrição do caso: {descricao_caso}"),
])

followup_pos_alta_prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um médico coordenador de follow-up pós-alta. Gere um plano de acompanhamento "
     "personalizado baseado na estratificação de risco. Inclua mensagem, orientações clínicas, "
     "sinais de alerta, prazo de retorno e canal de comunicação."),
    ("human", "Paciente: {nome}, {idade} anos\nDiagnóstico: {diagnostico}\n"
     "Risco: {risco}\nComorbidades: {comorbidades}\nDias pós-alta: {dias_pos_alta}"),
])

resumo_chain = resumo_prontuario_prompt | llm | StrOutputParser()
sumarizacao_chain = sumarizacao_evolucao_prompt | llm | StrOutputParser()
insights_chain = insights_dashboard_prompt | llm | StrOutputParser()
documentacao_chain = assistente_documentacao_prompt | llm | StrOutputParser()
regulatorio_chain = copilot_regulatorio_prompt | llm | StrOutputParser()
followup_chain = followup_pos_alta_prompt | llm | StrOutputParser()
