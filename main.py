import discord
from discord import app_commands, ui
from discord.ext import commands
import os
import psycopg2
from flask import Flask
from threading import Thread

# --- CONFIGURAÇÃO WEB ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot Online!"

def run_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURAÇÕES (VERIFIQUE SE OS IDs ESTÃO CERTOS) ---
TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

ID_CANAL_RECRUTAMENTO_LOGS = 1456450750241570887 
ID_CARGO_STAFF = 1411158389911715910 
ID_CANAL_ANON_PUBLICO = 1499100513902264351
ID_CANAL_ANON_LOGS = 1417278738390978681
ID_CANAL_LOGS_RP = 1465403347694522490
ID_CANAL_AVISO_VIGIA = 1499101802631528559
ID_CARGO_STAFF_AVISO = 1499102061705433249

URL_DO_CANAL_DE_TICKET = "COLE_AQUI_O_LINK_DO_CANAL"

# --- BANCO DE DADOS ---
def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS vigia (discord_id TEXT PRIMARY KEY)")
    conn.commit(); cur.close(); conn.close()

def db_manage(d_id, acao='add'):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    if acao == 'add': cur.execute("INSERT INTO vigia (discord_id) VALUES (%s) ON CONFLICT DO NOTHING", (str(d_id),))
    else: cur.execute("DELETE FROM vigia WHERE discord_id = %s", (str(d_id),))
    conn.commit(); conn.close()

def db_get_all():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(); cur.execute("SELECT discord_id FROM vigia")
    rows = cur.fetchall(); conn.close()
    return [row[0] for row in rows]

# --- 1. RECRUTAMENTO ---
class ModalRecusa(ui.Modal, title='Motivo da Reprovação'):
    motivo = ui.TextInput(label="Motivo", style=discord.TextStyle.paragraph)
    def __init__(self, membro): super().__init__(); self.membro = membro
    async def on_submit(self, interaction):
        try:
            emb = discord.Embed(title="❌ Reprovado", description=f"Motivo: {self.motivo.value}", color=discord.Color.red())
            await self.membro.send(embed=emb)
            await interaction.response.send_message("Recusado.", ephemeral=True)
            await interaction.message.edit(view=None)
        except: await interaction.response.send_message("DM Fechada.", ephemeral=True)

class ViewStaffRecrutamento(ui.View):
    def __init__(self, membro_id): super().__init__(timeout=None); self.membro_id = membro_id
    @ui.button(label="Aceitar", style=discord.ButtonStyle.success)
    async def aceitar(self, interaction, button):
        membro = interaction.guild.get_member(self.membro_id)
        if membro:
            try:
                emb = discord.Embed(title="🥳 Aprovado!", description=f"Abra um ticket aqui: {URL_DO_CANAL_DE_TICKET}", color=discord.Color.green())
                await membro.send(embed=emb)
                await interaction.response.send_message("Aprovado!", ephemeral=True)
                await interaction.message.edit(view=None)
            except: await interaction.response.send_message("DM Fechada.", ephemeral=True)

    @ui.button(label="Recusar", style=discord.ButtonStyle.danger)
    async def recusar(self, interaction, button):
        membro = interaction.guild.get_member(self.membro_id)
        await interaction.response.send_modal(ModalRecusa(membro))

class FormularioRecrutamento(ui.Modal, title='Recrutamento Raze RP'):
    p1 = ui.TextInput(label="Nome/Idade")
    p2 = ui.TextInput(label="Por que quer entrar?", style=discord.TextStyle.paragraph)
    async def on_submit(self, interaction):
        canal = interaction.guild.get_channel(ID_CANAL_RECRUTAMENTO_LOGS)
        embed = discord.Embed(title="📝 Nova Ficha", description=f"**Candidato:** {interaction.user.mention}\n1: {self.p1.value}\n2: {self.p2.value}", color=0xFF007F)
        await canal.send(embed=embed, view=ViewStaffRecrutamento(interaction.user.id))
        await interaction.response.send_message("Enviada!", ephemeral=True)

class ViewRecrutamentoFixo(ui.View):
    def __init__(self): super().__init__(timeout=None)
    @ui.button(label="📝 Iniciar Recrutamento", custom_id="rec_fixo", style=discord.ButtonStyle.danger)
    async def start(self, i, b): await i.response.send_modal(FormularioRecrutamento())

# --- 2. ANÔNIMO ---
class AnonModal(ui.Modal, title='Confissão'):
    msg = ui.TextInput(label='Mensagem', style=discord.TextStyle.paragraph)
    async def on_submit(self, interaction):
        await interaction.client.get_channel(ID_CANAL_ANON_PUBLICO).send(embed=discord.Embed(description=self.msg.value, color=0x2b2d31))
        await interaction.client.get_channel(ID_CANAL_ANON_LOGS).send(f"👤 **{interaction.user}** enviou: {self.msg.value}")
        await interaction.response.send_message("Enviado!", ephemeral=True)

class ViewAnonFixo(ui.View):
    def __init__(self): super().__init__(timeout=None)
    @ui.button(label="👤 Enviar Anônimo", custom_id="anon_fixo", style=discord.ButtonStyle.secondary)
    async def start(self, i, b): await i.response.send_modal(AnonModal())

# --- 3. VIGIA (COM MENÇÃO E LISTA) ---
class VigiaModal(ui.Modal):
    def __init__(self, acao): self.acao = acao; super().__init__(title="Gerenciar Vigia")
    d_id = ui.TextInput(label='ID do Discord')
    async def on_submit(self, interaction):
        db_manage(self.d_id.value, self.acao)
        await interaction.response.send_message(f"ID {'adicionado' if self.acao == 'add' else 'removido'}!", ephemeral=True)

class ViewVigiaFixo(ui.View):
    def __init__(self): super().__init__(timeout=None)
    @ui.button(label="🕵️ Vigiar ID", custom_id="v_add_fixo", style=discord.ButtonStyle.success)
    async def add(self, i, b): await i.response.send_modal(VigiaModal('add'))
    
    @ui.button(label="❌ Parar Vigia", custom_id="v_rem_fixo", style=discord.ButtonStyle.danger)
    async def rem(self, i, b): await i.response.send_modal(VigiaModal('remove'))

    @ui.button(label="📋 Ver Lista", custom_id="v_list_fixo", style=discord.ButtonStyle.secondary)
    async def list(self, i, b):
        ids = db_get_all()
        lista = "\n".join([f"<@{idd}> (`{idd}`)" for idd in ids]) if ids else "Nenhum ID monitorado."
        await i.response.send_message(f"**IDs sob vigilância:**\n{lista}", ephemeral=True)

# --- BOT CORE ---
class MeuBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def setup_hook(self):
        self.add_view(ViewRecrutamentoFixo())
        self.add_view(ViewAnonFixo())
        self.add_view(ViewVigiaFixo())
        init_db()

    async def on_message(self, message):
        if message.author == self.user: return
        await self.process_commands(message)
        if message.channel.id == ID_CANAL_LOGS_RP:
            conteudo = message.content.lower()
            for e in message.embeds: conteudo += f" {str(e.description).lower()} {str(e.title).lower()} "
            for d_id in db_get_all():
                if str(d_id) in conteudo:
                    await self.get_channel(ID_CANAL_AVISO_VIGIA).send(f"🚨 **ALVO LOGADO:** <@{d_id}> (`{d_id}`) entrou na cidade! <@&{ID_CARGO_STAFF_AVISO}>")

bot = MeuBot()

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_recrutamento(ctx): await ctx.send(embed=discord.Embed(title="RECRUTAMENTO"), view=ViewRecrutamentoFixo())

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_anonimo(ctx): await ctx.send(embed=discord.Embed(title="ANÔNIMO"), view=ViewAnonFixo())

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_vigia(ctx): await ctx.send(embed=discord.Embed(title="VIGILÂNCIA"), view=ViewVigiaFixo())

if __name__ == "__main__":
    Thread(target=run_server).start()
    bot.run(TOKEN)
