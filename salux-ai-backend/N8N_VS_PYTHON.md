# n8n vs Python + LangChain/LangGraph

Comparativo técnico entre as duas abordagens para o backend da Salux Health AI.

## Tabela comparativa

| Aspecto | n8n | Python + LangChain/LangGraph |
|---------|-----|-------------------------------|
| **Tipo** | Plataforma low-code de automação visual | Framework programático com grafos de estado |
| **Linguagem** | Visual + JavaScript (nós Code) | Python puro |
| **Curva de aprendizado** | Baixa — arrastar e soltar nós | Média-alta — requer Python, async, conceitos de grafo |
| **Velocidade de prototipação** | Alta — poucos minutos para conectar APIs | Média — precisa escrever código, testes, endpoints |
| **Performance** | 200–500ms de overhead por nó Code (VM2 isolada) | ~1–10ms para lógica determinística |
| **Custo de infraestrutura** | US$ 20–200/mês (Cloud) ou self-host (recursos) | Apenas VPS (~US$ 5–20/mês) |
| **Custo de desenvolvimento** | Menor no início — entrega rápida | Maior no início — setup + código |
| **Testes automatizados** | Limitado — só execução manual do workflow | pytest, CI/CD, cobertura de código |
| **Versionamento** | Export JSON do workflow (difícil de fazer diff/review) | Git normal (diff, PR, blame, review) |
| **Manutenção contínua** | Difícil — mudanças quebram nós visuais | Controlada — tipagem + testes previnem regressão |
| **Orquestração de agentes** | Limitada — switch/case + webhooks encadeados | StateGraph nativo com estados, loops, decisões |
| **Memória conversacional** | Manual — armazenar em variáveis | Checkpointer nativo (SQLite, PostgreSQL) |
| **Troca de LLM** | Fácil — trocar o nó OpenAI | Fácil — trocar provider no LangChain |
| **Debugar** | Abrir execução no navegador, clicar nós | breakpoint(), VS Code debugger, logs |
| **Escalabilidade** | Vertical (plano define limite) | Horizontal (vários workers uvicorn + load balancer) |
| **Vendor lock-in** | Alto — lógica, conectores e execução no ecossistema n8n | Baixo — Python roda em qualquer lugar |
| **Conectores prontos** | 400+ integrações nativas (Gmail, Slack, etc.) | Biblioteca Python padrão + requests para APIs |
| **Disponibilidade de profissionais** | Nicho — devs low-code | Massivo — maiores bootcamps e faculdades ensinam Python |
| **Monitoramento** | Dashboard nativo de execuções | Métricas customizadas (Prometheus, Grafana, logs) |

## Pontos positivos e negativos

### n8n

| ✅ Positivos | ❌ Negativos |
|-------------|-------------|
| Entrega rápida para integrações simples | Difícil de versionar (diff de JSON não é legível) |
| Baixa barreira técnica — equipe não-dev pode criar | Testes são manuais — não escala |
| 400+ conectores prontos | Performance baixa em nós com JS (VM2) |
| Visual — fácil entender o fluxo de longe | Manutenção complexa conforme o workflow cresce |
| Monitoramento embutido | Código JS solto dentro de nós — sem padrão |
| Ideal para prototipação e MVPs | Orquestração condicional vira "macarrão" de nós |

### Python + LangChain/LangGraph

| ✅ Positivos | ❌ Negativos |
|-------------|-------------|
| Código versionável com git (diff, PR, review) | Requer devs com conhecimento em Python |
| Testes automatizados com pytest | Setup inicial mais lento |
| Performance sem overhead (código nativo) | Curva de aprendizado maior (LangGraph, async) |
| Orquestração complexa com StateGraph | Precisa construir monitoramento do zero |
| Sem vendor lock-in — roda em qualquer infra | Menos conectores prontos (precisa implementar) |
| Debugger profissional (VS Code, breakpoints) | Documentação de LangGraph ainda em evolução |
| Tipagem estática com Pydantic | Python 3.14 tem incompatibilidades com Pydantic v1 |
| O mais usado no mercado de IA/LLMs | |

## Credenciais e segurança

| Aspecto | n8n | Python + LangChain/LangGraph |
|---------|-----|-------------------------------|
| **Armazenamento de secrets** | Cofre criptografado interno (banco n8n) | `.env` ou vault externo (HashiCorp Vault, AWS Secrets Manager) |
| **Chave de API no código** | Fica no nó credential — criptografada em repouso | Fica no `.env` — fora do código fonte |
| **Vazar secret por acidente** | Difícil — UI não expõe o valor depois de salvo | Fácil — commitar `.env` ou hardcoded no código |
| **Controle de acesso** | RBAC nativo (owner, member, —) | Feito na aplicação (FastAPI middleware, OAuth2, JWT) |
| ** Auditoria de quem alterou** | Log de execuções do workflow | Git log + sistema de auth próprio |
| **Criptografia em trânsito** | Depende do deploy (HTTPS via proxy) | Depende do deploy (HTTPS via proxy/TLS) |
| **Criptografia em repouso** | Secrets criptografados no banco n8n | Secrets em texto plano no `.env` (precisa de vault externo) |
| **Isolamento de execução** | Cada execução é isolada (sandbox leve) | Cada request é isolado (async Python) |
| **Sanitização de input** | Automática nos nós HTTP/Webhook | Manual — precisa validar com Pydantic |
| **Proteção contra injeção** | Bailey — nós tratam escaping automaticamente | Manual — SQL injection, command injection etc. |
| **Rotação de chaves** | Trocar no nó credential — impacto imediato | Trocar no `.env` + restart do servidor |
| **Exposição em logs** | UI não loga valores de credential | Precisa cuidado para não logar secrets |
| **Certificações (SOC2, HIPAA)** | n8n Cloud tem SOC2 | Responsabilidade do time — implementar do zero |

### n8n

| ✅ Positivos | ❌ Negativos |
|-------------|-------------|
| Cofre criptografado nativo para secrets | Secrets ficam no banco n8n — se invadirem o n8n, tudo exposto |
| RBAC pronto para times | Permissão granular limitada (só owner/member) |
| Auditoria de execuções embutida | Não tem auditoria de alteração de credential fora do log |
| UI não expõe valor da credential depois de salva | Depende do self-host para criptografia em trânsito |
| Fácil de ro tear — editar no nó e salvar | Rotação não versionada — sem trilha de quem/quando trocou |

### Python + FastAPI

| ✅ Positivos | ❌ Negativos |
|-------------|-------------|
| Secrets fora do código (`.env`) — nunca no git se bem configurado | Fácil de cometer o erro de subir `.env` para o repo |
| Pode integrar vault profissional (HashiCorp, AWS, Azure) | Setup de vault é complexo e custa infra |
| Validação com Pydantic — tipagem forte evita injeção | Validação é manual — esquecer expõe a aplicação |
| Git log audita cada alteração de código | Não audita acesso a secrets em produção |
| Controle de acesso total via middleware | Precisa implementar do zero (JWT, OAuth2, RBAC) |
| Roda atrás de qualquer proxy (nginx, Cloudflare) | Responsabilidade total do time pela segurança |

### Resumo segurança

| Situação | Risco menor em |
|----------|---------------|
| Vazar secrets por acidente (commit) | n8n — UI não expõe valor salvo |
| Auditoria de código e alterações | Python — git history completo |
| Controle de acesso granular | Python — implementação customizada |
| Setup rápido com segurança básica | n8n — cofre e RBAC nativos |
| Compliance (HIPAA, SOC2, LGPD) | Python — controle total para certificar |
| Equipe pequena sem devops dedicado | n8n — menos responsabilidade de segurança |

A principal diferença: no n8n a segurança vem "embutida" mas você não controla os detalhes. Em Python você tem controle total, mas precisa implementar (ou pagar) cada camada.
## Quando usar cada um

| Cenário | Recomendação |
|---------|-------------|
| Conectar Slack + Gmail + Sheets rapidamente | n8n |
| Workflow com < 5 etapas e sem lógica complexa | n8n |
| Equipe não-técnica precisa criar/alterar fluxos | n8n |
| Prova de conceito / MVP em dias | n8n |
| **Algoritmos de scoring e regras de negócio** | **Python** |
| **Chat com memória e estado (agentes)** | **Python + LangGraph** |
| **Testes automatizados obrigatórios** | **Python** |
| **Time de engenharia mantendo o código** | **Python** |
| **Múltiplos LLMs e troca frequente de provedor** | **Python + LangChain** |
| **Escalar horizontalmente em produção** | **Python + FastAPI** |

## Números reais do projeto Salux

| Métrica | n8n (antes) | Python (depois) |
|---------|-------------|-----------------|
| Workflows | 14 | 14 (reescritos) |
| Testes automatizados | 0 | 4 (scoring) + expansão |
| Linhas de código backend | ~30 nós visuais + ~600 linhas JS | ~800 linhas Python |
| Tempo médio scoring | ~300ms (com overhead n8n) | ~5ms |
| Dependências externas | n8n Cloud + Docker | Python + pip |
