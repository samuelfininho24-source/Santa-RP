import discord
from discord import app_commands
import json, os, asyncio

TOKEN=os.getenv("TOKEN")
FILE="ids.json"
MAX_ID=1000
intents=discord.Intents.default()
intents.members=True
class SantaBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree=app_commands.CommandTree(self)
        self.lock=asyncio.Lock()
bot=SantaBot()

def load():
    if not os.path.exists(FILE):
        save({"ultimo_id":-1,"usuarios":{}})
    try:
        with open(FILE,"r",encoding="utf-8") as f: return json.load(f)
    except: return {"ultimo_id":-1,"usuarios":{}}

def save(data):
    with open(FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=4,ensure_ascii=False)

def fid(n): return f"{n:02d}" if n<100 else str(n)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Santa Bot online: {bot.user}")

@bot.tree.command(name="id",description="Receba seu ID do servidor.")
async def id_cmd(interaction: discord.Interaction):
    async with bot.lock:
        data=load()
        uid=str(interaction.user.id)
        if uid in data["usuarios"]:
            mid=data["usuarios"][uid]
            existing=True
        else:
            n=data["ultimo_id"]+1
            if n>MAX_ID:
                await interaction.response.send_message("❌ Todos os IDs de 00 até 1000 já foram distribuídos.")
                return
            mid=fid(n)
            data["ultimo_id"]=n
            data["usuarios"][uid]=mid
            save(data)
            existing=False

    name=interaction.user.display_name
    if "|" in name: name=name.split("|",1)[1].strip()
    renamed=False
    try:
        await interaction.user.edit(nick=f"{mid} | {name}"[:32])
        renamed=True
    except (discord.Forbidden,discord.HTTPException): pass

    title="🆔 SANTA BOT" if existing else "🎉 ID ATRIBUÍDO"
    desc=(f"{interaction.user.mention} já possui o ID **`{mid}`**."
          if existing else
          f"🎉 {interaction.user.mention} recebeu o ID **`{mid}`**!")
    e=discord.Embed(title=title,description=desc,color=discord.Color.blue())
    if not renamed:
        e.add_field(name="⚠️ Apelido",value="Não consegui alterar o apelido. O ID foi salvo.",inline=False)
    e.set_footer(text="Santa Bot • Sistema de IDs")
    # RESPOSTA PÚBLICA: não usa ephemeral=True.
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="meuid",description="Veja seu ID.")
async def meuid(interaction: discord.Interaction):
    data=load(); uid=str(interaction.user.id)
    if uid not in data["usuarios"]:
        await interaction.response.send_message("❌ Você ainda não possui um ID. Use `/id`.")
        return
    await interaction.response.send_message(f"🆔 {interaction.user.mention}, seu ID é **`{data['usuarios'][uid]}`**.")

@bot.tree.command(name="idstatus",description="Veja o status dos IDs.")
@app_commands.default_permissions(administrator=True)
async def status(interaction: discord.Interaction):
    data=load(); last=data["ultimo_id"]
    await interaction.response.send_message(
        f"📊 **Santa Bot**\nIDs distribuídos: `{len(data['usuarios'])}`\n"
        f"Último: `{fid(last) if last>=0 else 'Nenhum'}`\n"
        f"Próximo: `{fid(last+1) if last<MAX_ID else 'Esgotado'}`"
    )

if not TOKEN: raise RuntimeError("Configure TOKEN no Railway.")
bot.run(TOKEN)
