import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from httpx import AsyncClient
from src.config import settings

logger = logging.getLogger(__name__)
N8N_API = "http://localhost:5678/webhook"

COMMAND_MAP = {
    "start": None,
    "doc": ("salux-assistente-documentacao", "texto_clinico"),
    "reg": ("salux-copilot-regulatorio", "descricao_caso"),
    "ask": ("salux-copiloto-conversacional", "pergunta"),
}


def format_response(wf_name: str, data: dict) -> str:
    if wf_name == "salux-assistente-documentacao":
        texto = data.get("texto_evolucao", data.get("output", {}).get("texto_evolucao", ""))
        return f"📋 *Assistente de Documentação Clínica*\n\n{texto}"
    if wf_name == "salux-copilot-regulatorio":
        just = data.get("justificativa", data.get("output", {}).get("justificativa", ""))
        return f"📄 *Copilot Regulatório*\n\n{just}"
    return f"💬 *Resposta:*\n{data.get('resposta', str(data))}"


async def start_bot():
    if not settings.telegram_bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN não configurado. Bot Telegram desabilitado.")
        return

    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()
    client = AsyncClient()

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer(
            "🤖 *Salux Health AI Bot*\n\n"
            "Comandos disponíveis:\n"
            "/doc - Assistente de Documentação Clínica\n"
            "/reg - Copilot Regulatório\n"
            "/ask - Copiloto Conversacional\n"
            "/dashboard <comando> - Dashboard por voz",
            parse_mode="Markdown",
        )

    @dp.message(Command("doc", "reg", "ask"))
    async def cmd_workflow(message: types.Message):
        cmd = message.text.split()[0][1:]
        wf_name, field = COMMAND_MAP[cmd]
        payload_text = message.text.replace(f"/{cmd}", "", 1).strip()

        if not payload_text:
            await message.answer("Envie o texto junto com o comando.")
            return

        payload = {field: payload_text}
        if cmd == "ask":
            payload["perfil"] = "executivo"

        resp = await client.post(f"{N8N_API}/{wf_name}", json=payload)
        data = resp.json()
        await message.answer(format_response(wf_name, data), parse_mode="Markdown")

    @dp.message(Command("dashboard"))
    async def cmd_dashboard(message: types.Message):
        comando = message.text.replace("/dashboard", "", 1).strip()
        if not comando:
            await message.answer("Exemplo: /dashboard status do hospital")
            return

        resp = await client.post(f"{N8N_API}/salux-dashboard-voz", json={"comando": comando})
        data = resp.json()
        await message.answer(format_response("dashboard", data), parse_mode="Markdown")

    logger.info("Bot Telegram iniciado (polling)")
    await dp.start_polling(bot)
