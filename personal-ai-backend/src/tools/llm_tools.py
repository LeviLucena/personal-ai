from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.config import settings

llm = ChatOpenAI(model=settings.openai_model, temperature=0.1)

resumo_prontuario_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an intensivist physician specialized in medical record summarization. "
     "Generate a concise clinical summary and identify critical alerts."),
    ("human", "Patient: {nome}, {idade} years\nDiagnoses: {diagnosticos}\n"
     "Allergies: {alergias}\nTests: {exames}\nProgress: {evolucao}"),
])

sumarizacao_evolucao_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an intensivist physician. Summarize the clinical progress of the last {dias} days. "
     "Identify: period summary, main complications, clinical trend "
     "(IMPROVING/STABLE/WORSENING), procedures performed, next steps, and current risk."),
    ("human", "{evolucao}"),
])

insights_dashboard_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a healthcare data analyst. Analyze the KPIs and generate:\n"
     "1. Executive summary\n2. Insights with status and suggested action for each indicator\n"
     "3. Intervention priority (sorted by criticality)"),
    ("human", "{kpis}"),
])

assistente_documentacao_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a physician specialized in clinical documentation. Based on the clinical context "
     "and the text dictated by the doctor, return ONLY a valid JSON (no markdown, no ```) "
     "with this exact structure:\n"
     '{{\n'
     '  "texto_evolucao_sugerido": "complete progress note text",\n'
     '  "qualidade_estimada": "HIGH" or "MEDIUM" or "LOW",\n'
     '  "evolucao_estruturada": {{\n'
     '    "subjetivo": "patient complaints",\n'
     '    "objetivo": "physical exam findings",\n'
     '    "avaliacao": "clinical analysis",\n'
     '    "plano": "management and prescriptions"\n'
     '  }},\n'
     '  "campos_preenchidos": ["field1", "field2"],\n'
     '  "campos_faltantes": ["field1", "field2"],\n'
     '  "cids_sugeridos": ["ICD1", "ICD2"],\n'
     '  "alertas_documentacao": ["alert1", "alert2"]\n'
     "}}"),
    ("human", "Clinical context: {contexto}\n\nDoctor's text: {texto_clinico}"),
])

copilot_regulatorio_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a specialist in medical regulation/authorization. "
     "Based on the case description, return ONLY a valid JSON (no markdown, no ```) "
     "with this exact structure:\n"
     '{{\n'
     '  "justificativa_clinica": "complete justification text",\n'
     '  "argumentos_principais": ["arg1", "arg2", ...],\n'
     '  "embasamento_cientifico": ["ref1", "ref2", ...],\n'
     '  "documentos_necessarios": ["doc1", "doc2", ...],\n'
     '  "pontos_atencao": ["point1", "point2", ...],\n'
     '  "probabilidade_aprovacao": 85\n'
     "}}"),
    ("human", "Case description: {descricao_caso}"),
])

followup_pos_alta_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a post-discharge follow-up coordinator physician. Generate a personalized follow-up "
     "plan based on risk stratification. Include message, clinical guidance, warning signs, "
     "return timeframe, and communication channel."),
    ("human", "Patient: {nome}, {idade} years\nDiagnosis: {diagnostico}\n"
     "Risk: {risco}\nComorbidities: {comorbidades}\nDays post-discharge: {dias_pos_alta}"),
])

resumo_chain = resumo_prontuario_prompt | llm | StrOutputParser()
sumarizacao_chain = sumarizacao_evolucao_prompt | llm | StrOutputParser()
insights_chain = insights_dashboard_prompt | llm | StrOutputParser()
documentacao_chain = assistente_documentacao_prompt | llm | StrOutputParser()
regulatorio_chain = copilot_regulatorio_prompt | llm | StrOutputParser()
followup_chain = followup_pos_alta_prompt | llm | StrOutputParser()
