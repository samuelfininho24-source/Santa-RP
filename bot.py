import discord
from discord import app_commands
import json
import os
import sys

# =========================================================
# SANTA BOT - SISTEMA DE ID
# IDs: 00 até 1000
# Comando: /id
# =========================================================

TOKEN = os.getenv("TOKEN")
ARQUIVO = "ids.json"

if not TOKEN:
    print("ERRO: a variável TOKEN não foi configurada no Railway.")
    sys.exit(1)

# Cria o arquivo de IDs se ele ainda não existir.
if not os.path.exists(ARQUIVO):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(
            {"ultimo_id": -1, "usuarios": {}},
            f,
            indent=4,
            ensure_ascii=False
        )


def carregar_ids():
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        dados = {"ultimo_id": -1, "usuarios": {}}
        salvar_ids(dados)
        return dados


def salvar_ids(dados):
    # Grava primeiro em um arquivo temporário para reduzir
    # a chance de corromper o JSON durante uma gravação.
    temporario = ARQUIVO + ".tmp"

    with open(temporario, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

    os.replace(temporario, ARQUIVO)


intents = discord.Intents.default()
intents.members = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)


@bot.event
async def on_ready():
    try:
        await tree.sync()
        print("Comandos slash sincronizados.")
    except Exception as erro:
        print(f"Erro ao sincronizar comandos: {erro}")

    print("====================================")
    print("         SANTA BOT ONLINE")
    print("====================================")
    print(f"Bot: {bot.user}")
    print("Comando: /id")
    print("IDs: 00 até 1000")
    print("====================================")


@tree.command(
    name="id",
    description="Receba seu ID do servidor."
)
async def id_command(interaction: discord.Interaction):
    dados = carregar_ids()
    usuario_id = str(interaction.user.id)

    # Se já possui ID, devolve o mesmo ID.
    if usuario_id in dados["usuarios"]:
        meu_id = dados["usuarios"][usuario_id]

        embed = discord.Embed(
            title="🆔 SANTA BOT",
            description=(
                "Você já possui um ID registrado!\n\n"
                f"🆔 **Seu ID:** `{meu_id}`"
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Santa Bot • Sistema de IDs")

        await interaction.response.send_message(
            embed=embed,
            ephemeral=False
        )
        return

    # Próximo ID.
    novo_id = dados["ultimo_id"] + 1

    # Limite: 1000.
    if novo_id > 1000:
        embed = discord.Embed(
            title="❌ SANTA BOT",
            description=(
                "Todos os IDs disponíveis já foram utilizados.\n"
                "O limite é **1000**."
            ),
            color=discord.Color.red()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=False
        )
        return

    # 0 -> 00, 1 -> 01 ... 99 -> 99, 100 -> 100.
    meu_id = f"{novo_id:02d}" if novo_id < 100 else str(novo_id)

    # Registra o ID.
    dados["ultimo_id"] = novo_id
    dados["usuarios"][usuario_id] = meu_id
    salvar_ids(dados)

    # Tenta colocar o ID no apelido.
    apelido_alterado = False

    try:
        nome_atual = interaction.user.display_name

        # Remove um possível ID anterior do apelido.
        if "|" in nome_atual:
            nome_atual = nome_atual.split("|", 1)[1].strip()

        novo_nome = f"{meu_id} | {nome_atual}"[:32]

        await interaction.user.edit(nick=novo_nome)
        apelido_alterado = True

    except discord.Forbidden:
        pass
    except discord.HTTPException:
        pass

    embed = discord.Embed(
        title="🆔 SANTA BOT",
        description=(
            "Seu ID foi registrado com sucesso!\n\n"
            f"🆔 **Seu ID:** `{meu_id}`\n"
            f"👤 **Membro:** {interaction.user.mention}"
        ),
        color=discord.Color.blue()
    )

    if apelido_alterado:
        embed.add_field(
            name="✅ Apelido",
            value=f"`{meu_id} | {nome_atual}`",
            inline=False
        )
    else:
        embed.add_field(
            name="⚠️ Apelido não alterado",
            value=(
                "O ID foi salvo normalmente, mas não consegui alterar "
                "seu apelido. Dê ao bot a permissão **Gerenciar Apelidos** "
                "e deixe o cargo dele acima do usuário."
            ),
            inline=False
        )

    embed.set_footer(text="Santa Bot • Sistema de IDs")

    await interaction.response.send_message(
        embed=embed,
        ephemeral=False
    )


bot.run(TOKEN)
