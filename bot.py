import discord
from discord import app_commands
import json
import os
import asyncio

TOKEN = os.getenv("TOKEN")
DATA_FILE = "ids.json"
MAX_ID = 1000

intents = discord.Intents.default()
intents.members = True

class SantaBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.lock = asyncio.Lock()

bot = SantaBot()

def load_data():
    if not os.path.exists(DATA_FILE):
        data = {"ultimo_id": -1, "usuarios": {}}
        save_data(data)
        return data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("ultimo_id", -1)
        data.setdefault("usuarios", {})
        return data
    except (json.JSONDecodeError, OSError):
        return {"ultimo_id": -1, "usuarios": {}}

def save_data(data):
    temp = DATA_FILE + ".tmp"
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    os.replace(temp, DATA_FILE)

def format_id(number):
    return f"{number:02d}" if number < 100 else str(number)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Santa Bot online: {bot.user} ({bot.user.id})")
    print("Comando /id sincronizado.")

@bot.tree.command(name="id", description="Receba seu ID do servidor.")
async def id_command(interaction: discord.Interaction):
    async with bot.lock:
        data = load_data()
        user_key = str(interaction.user.id)

        if user_key in data["usuarios"]:
            assigned_id = data["usuarios"][user_key]
            already_had = True
        else:
            next_number = data["ultimo_id"] + 1
            if next_number > MAX_ID:
                await interaction.response.send_message(
                    "❌ Todos os IDs de 00 até 1000 já foram distribuídos.",
                    ephemeral=True
                )
                return

            assigned_id = format_id(next_number)
            data["ultimo_id"] = next_number
            data["usuarios"][user_key] = assigned_id
            save_data(data)
            already_had = False

    nickname_ok = False
    try:
        current_name = interaction.user.display_name
        if "|" in current_name:
            current_name = current_name.split("|", 1)[1].strip()
        new_nickname = f"{assigned_id} | {current_name}"[:32]
        await interaction.user.edit(nick=new_nickname)
        nickname_ok = True
    except (discord.Forbidden, discord.HTTPException):
        pass

    embed = discord.Embed(
        title="🆔 SANTA BOT",
        description=(
            f"Seu ID {'já está registrado' if already_had else 'foi registrado com sucesso'}!\n\n"
            f"**ID:** `{assigned_id}`\n"
            f"**Membro:** {interaction.user.mention}"
        ),
        color=discord.Color.blue()
    )

    if nickname_ok:
        embed.add_field(
            name="👤 Apelido",
            value=f"`{assigned_id} | {current_name}`",
            inline=False
        )
    else:
        embed.add_field(
            name="⚠️ Apelido",
            value="Não consegui alterar seu apelido. O ID continua salvo normalmente.",
            inline=False
        )

    embed.set_footer(text="Santa Bot • Sistema de IDs")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="meuid", description="Veja o seu ID registrado.")
async def meuid_command(interaction: discord.Interaction):
    data = load_data()
    user_key = str(interaction.user.id)

    if user_key not in data["usuarios"]:
        await interaction.response.send_message(
            "❌ Você ainda não possui um ID. Use `/id`.",
            ephemeral=True
        )
        return

    assigned_id = data["usuarios"][user_key]
    embed = discord.Embed(
        title="🆔 SEU ID",
        description=f"Seu ID é **`{assigned_id}`**.",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="idstatus", description="Veja quantos IDs já foram distribuídos.")
@app_commands.default_permissions(administrator=True)
async def idstatus_command(interaction: discord.Interaction):
    data = load_data()
    total = len(data["usuarios"])
    ultimo = data["ultimo_id"]

    embed = discord.Embed(
        title="📊 SANTA BOT • STATUS",
        description=(
            f"**IDs distribuídos:** `{total}`\n"
            f"**Último número:** `{format_id(ultimo) if ultimo >= 0 else 'Nenhum'}`\n"
            f"**Próximo ID:** `{format_id(ultimo + 1) if ultimo < MAX_ID else 'Esgotado'}`\n"
            f"**Limite:** `1000`"
        ),
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

if not TOKEN:
    raise RuntimeError("Configure a variável TOKEN no Railway.")

bot.run(TOKEN)
