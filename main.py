import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- MANTER ONLINE ---
app = Flask('')
@app.route('/')
def home(): return "Bot Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CONFIGURAÇÕES ---
TOKEN = os.getenv("DISCORD_TOKEN")
ID_CANAL_LOG = 1456450750241570887 # <--- SEU ID DE CANAL AQUI
ID_CARGO_STAFF = 1411158389911715910 # <--- COLOQUE O ID DO CARGO QUE O PLAYER VAI GANHAR AO SER ACEITO

# --- MODAL DE MOTIVO DA RECUSA ---
class ModalRecusa(discord.ui.Modal, title='Motivo da Reprovação'):
    motivo = discord.ui.TextInput(label="Por que ele foi recusado?", style=discord.TextStyle.paragraph, placeholder="Ex: Idade insuficiente ou falta de conhecimento das regras.")

    def __init__(self, membro_candidato):
        super().__init__()
        self.membro_candidato = membro_candidato

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await self.membro_candidato.send(f"❌ **Recrutamento Raze Roleplay**\nInfelizmente você foi reprovado.\n**Motivo:** {self.motivo.value}")
            await interaction.response.send_message(f"Candidato {self.membro_candidato.mention} recusado e avisado no PV.", ephemeral=True)
            # Desativa os botões da mensagem original
            await interaction.message.edit(view=None)
        except:
            await interaction.response.send_message("O candidato está com o PV fechado, mas a recusa foi registrada.", ephemeral=True)

# --- VIEW COM BOTÕES DE ACEITAR/RECUSAR ---
class ViewStaff(discord.ui.View):
    def __init__(self, membro_id):
        super().__init__(timeout=None)
        self.membro_id = membro_id

    @discord.ui.button(label="Aceitar", style=discord.ButtonStyle.success, custom_id="aceitar_btn")
    async def aceitar(self, interaction: discord.Interaction, button: discord.ui.Button):
        membro = interaction.guild.get_member(self.membro_id)
        cargo = interaction.guild.get_role(ID_CARGO_STAFF)
        
        if membro and cargo:
            await membro.add_roles(cargo)
            try:
                await membro.send(f"🥳 **Parabéns!** Você foi aceito na Staff do **Raze Roleplay**!\nO cargo **{cargo.name}** já foi adicionado a você.")
            except: pass
            await interaction.response.send_message(f"✅ {membro.mention} foi aceito e recebeu o cargo!", ephemeral=True)
            await interaction.message.edit(view=None)
        else:
            await interaction.response.send_message("Erro: Membro ou Cargo não encontrado.", ephemeral=True)

    @discord.ui.button(label="Recusar", style=discord.ButtonStyle.danger, custom_id="recusar_btn")
    async def recusar(self, interaction: discord.Interaction, button: discord.ui.Button):
        membro = interaction.guild.get_member(self.membro_id)
        if membro:
            await interaction.response.send_modal(ModalRecusa(membro))
        else:
            await interaction.response.send_message("Membro não encontrado no servidor.", ephemeral=True)

# --- FORMULÁRIO DE PERGUNTAS (Simplificado para evitar o erro do log) ---
class FormularioRecrutamento(discord.ui.Modal, title='Recrutamento Staff'):
    p1 = discord.ui.TextInput(label="Nome e Idade", min_length=3)
    p2 = discord.ui.TextInput(label="Por que quer ser Staff?", style=discord.TextStyle.paragraph)
    p3 = discord.ui.TextInput(label="Experiência anterior?", placeholder="Sim/Não, onde?")
    p4 = discord.ui.TextInput(label="Disponibilidade diária", placeholder="Ex: 4 a 6 horas")
    p5 = discord.ui.TextInput(label="O que faria em caso de RDM?", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        canal_log = interaction.guild.get_channel(ID_CANAL_LOG)
        embed = discord.Embed(title="📝 Nova Ficha de Recrutamento", color=0xFF007F)
        embed.add_field(name="Candidato:", value=interaction.user.mention)
        embed.add_field(name="Respostas:", value=f"1: {self.p1.value}\n2: {self.p2.value}\n3: {self.p3.value}\n4: {self.p4.value}\n5: {self.p5.value}")
        
        await canal_log.send(embed=embed, view=ViewStaff(interaction.user.id))
        await interaction.response.send_message("✅ Seu formulário foi enviado com sucesso!", ephemeral=True)

# --- RESTANTE DO CÓDIGO (BOT) ---
class BotaoInicio(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="📝 Iniciar Recrutamento", style=discord.ButtonStyle.danger, custom_id="init_btn")
    async def iniciar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FormularioRecrutamento())

class MeuBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
    async def setup_hook(self): self.add_view(BotaoInicio())

bot = MeuBot()

@bot.command()
@commands.has_permissions(administrator=True)
async def postar(ctx):
    embed = discord.Embed(title="RAZE ROLEPLAY | RECRUTAMENTO", description="Clique no botão abaixo para iniciar.", color=0xFF007F)
    await ctx.send(embed=embed, view=BotaoInicio())

keep_alive()
bot.run(TOKEN)
