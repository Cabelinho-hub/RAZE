import discord
from discord import app_commands, ui
from discord.ext import commands
import os
import psycopg2
from flask import Flask
from threading import Thread
from datetime import datetime

# --- CONFIGURAÇÃO WEB (Flask para o Render) ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot Online!"

def run_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURAÇÕES DOS CANAIS E CARGOS (PREENCHA AQUI) ---
TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

ID_CANAL_RECRUTAMENTO_LOGS = 1456450750241570887 
ID_CARGO_STAFF = 1411158389911715910 

ID_CANAL_ANON_PUBLICO = 0000  # Canal onde as confissões aparecem
ID_CANAL_ANON_LOGS = 0000     # Onde staff vê quem mandou o anônimo
ID_CANAL_LOGS_RP = 0000       # Canal onde o bot da cidade avisa quem entrou
ID_CANAL_AVISO_VIGIA = 0000   # Onde seu bot avisa que o alvo entrou
ID_CARGO_STAFF_AVISO = 0000   # Cargo marcado no aviso de vigia

# --- CONEXÃO BANCO DE DADOS (Vigia Permanente) ---
def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS vigia (discord_id TEXT PRIMARY KEY)")
    conn.commit()
    cur.close()
    conn.close()

def db_manage(d_id, acao='add'):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    if acao == 'add':
        cur.execute("INSERT INTO vigia (discord_id) VALUES (%s) ON CONFLICT DO NOTHING", (str(d_id),))
    else:
        cur.execute("DELETE FROM vigia WHERE discord_id = %s", (str(d_id),))
    conn.commit()
    conn.close()

def db_get_all():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT discord_id FROM vigia")
    ids = {row[0] for row in cur.fetchall()}
    conn.close()
    return ids

# --- MODAIS (ANÔNIMO E VIGIA) ---
class AnonModal(ui.Modal, title='Mensagem Anônima'):
    msg = ui.TextInput(label='Sua Mensagem', style=discord.TextStyle.paragraph)
    async def on_submit(self, interaction):
        pub = interaction.client.get_channel(ID_CANAL_ANON_PUBLICO)
        logs = interaction.client.get_channel(ID_CANAL_ANON_LOGS)
        await pub.send(embed=discord.Embed(description=self.msg.value, color=0x2b2d31))
        await logs.send(f"👤 **{interaction.user}** ({interaction.user.id}) enviou: {self.msg.value}")
        await interaction.response.send_message("Enviado anonimamente!", ephemeral=True)

class VigiaModal(ui.Modal):
    def __init__(self, acao):
        self.acao = acao
        super().__init__(title="Gerenciar Vigia")
    d_id = ui.TextInput(label='ID do Discord do Alvo')
    async def on_submit(self, interaction):
        db_manage(self.d_id.value, self.acao)
        await interaction.response.send_message(f"ID {self.d_id.value} {'adicionado' if self.acao == 'add' else 'removido'}!", ephemeral=True)

# --- RECRUTAMENTO (SEU CÓDIGO ORIGINAL) ---
class ModalRecusa(ui.Modal, title='Motivo da Reprovação'):
    motivo = ui.TextInput(label="Por que ele foi recusado?", style=discord.TextStyle.paragraph)
    def __init__(self, membro_candidato):
        super().__init__()
        self.membro_candidato = membro_candidato
    async def on_submit(self, interaction):
        await self.membro_candidato.send(f"❌ Reprovado no Raze RP.\nMotivo: {self.motivo.value}")
        await interaction.response.send_message("Candidato recusado.", ephemeral=True)

class ViewStaffRecrutamento(ui.View):
    def __init__(self, membro_id):
        super().__init__(timeout=None)
        self.membro_id = membro_id
    @ui.button(label="Aceitar", style=discord.ButtonStyle.success)
    async def aceitar(self, interaction, button):
        membro = interaction.guild.get_member(self.membro_id)
        await membro.add_roles(interaction.guild.get_role(ID_CARGO_STAFF))
        await interaction.response.send_message("Aceito!", ephemeral=True)

class FormularioRecrutamento(ui.Modal, title='Recrutamento Staff'):
    p1 = ui.TextInput(label="Nome e Idade")
    p2 = ui.TextInput(label="Por que quer ser Staff?", style=discord.TextStyle.paragraph)
    async def on_submit(self, interaction):
        canal = interaction.guild.get_channel(ID_CANAL_RECRUTAMENTO_LOGS)
        embed = discord.Embed(title="Nova Ficha", description=f"De: {interaction.user.mention}\n1: {self.p1.value}\n2: {self.p2.value}", color=0xFF007F)
        await canal.send(embed=embed, view=ViewStaffRecrutamento(interaction.user.id))
        await interaction.response.send_message("Ficha enviada!", ephemeral=True)

# --- PAINEL PRINCIPAL ---
class MainView(ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @ui.button(label="📝 Recrutamento", custom_id="btn_rec", style=discord.ButtonStyle.danger)
    async def rec(self, i, b): await i.response.send_modal(FormularioRecrutamento())
    
    @ui.button(label="👤 Anônimo", custom_id="btn_anon", style=discord.ButtonStyle.secondary)
    async def anon(self, i, b): await i.response.send_modal(AnonModal())
    
    @ui.button(label="🕵️ Vigiar ID", custom_id="btn_v_add", style=discord.ButtonStyle.success)
    async def v_add(self, i, b): await i.response.send_modal(VigiaModal('add'))

    @ui.button(label="❌ Parar Vigia", custom_id="btn_v_rem", style=discord.ButtonStyle.secondary)
    async def v_rem(self, i, b): await i.response.send_modal(VigiaModal('remove'))

# --- BOT SETUP ---
class MeuBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(MainView())
        init_db()

    async def on_message(self, message):
        if message.author == self.user: return
        if message.channel.id == ID_CANAL_LOGS_RP:
            conteudo = message.content.lower()
            for e in message.embeds: conteudo += f" {e.description} {e.title}"
            for d_id in db_get_all():
                if d_id in conteudo:
                    await self.get_channel(ID_CANAL_AVISO_VIGIA).send(f"🚨 **ALVO LOGADO:** `{d_id}` <@&{ID_CARGO_STAFF_AVISO}>")

bot = MeuBot()

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(title="RAZE ROLEPLAY | CENTRAL", description="Escolha uma opção abaixo.", color=0xFF007F)
    await ctx.send(embed=embed, view=MainView())

# --- INICIALIZAÇÃO ---
if __name__ == "__main__":
    Thread(target=run_server).start()
    bot.run(TOKEN)
