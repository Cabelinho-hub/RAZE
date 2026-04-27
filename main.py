import discord
import os
from discord.ext import commands
from discord import app_commands

# --- CONFIGURAÇÕES ---
TOKEN = os.getenv("DISCORD_TOKEN")
ID_CANAL_LOG = 1456450750241570887 
ID_CARGO_STAFF = 1411158389911715910 

# 1. MODAL PARA O MOTIVO DA RECUSA
class ModalMotivoRecusa(discord.ui.Modal, title='Motivo da Rejeição'):
    motivo = discord.ui.TextInput(
        label="Descreva o motivo da recusa:",
        style=discord.TextStyle.paragraph,
        placeholder="Ex: Você não atingiu a idade mínima.",
        required=True
    )

    def __init__(self, candidato):
        super().__init__()
        self.candidato = candidato

    async def on_submit(self, interaction: discord.Interaction):
        try:
            embed = discord.Embed(title="Atualização de Recrutamento", color=discord.Color.red())
            embed.description = f"Olá, seu formulário em **{interaction.guild.name}** foi recusado.\n\n**Motivo:** {self.motivo.value}"
            await self.candidato.send(embed=embed)
            
            await interaction.response.send_message(f"❌ {self.candidato.display_name} foi recusado e avisado.", ephemeral=True)
            await interaction.message.edit(view=None)
        except discord.Forbidden:
            await interaction.response.send_message(f"⚠️ Recusado, mas não consegui enviar DM para {self.candidato.mention}.", ephemeral=True)

# 2. VIEW COM OS BOTÕES DE ACEITAR/RECUSAR (PARA A STAFF)
class ViewStaff(discord.ui.View):
    def __init__(self, candidato_id):
        super().__init__(timeout=None)
        self.candidato_id = candidato_id

    @discord.ui.button(label="Aceitar", style=discord.ButtonStyle.success)
    async def aceitar(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        candidato = guild.get_member(self.candidato_id)
        cargo = guild.get_role(ID_CARGO_STAFF)

        if candidato and cargo:
            await candidato.add_roles(cargo)
            await interaction.response.send_message(f"✅ {candidato.mention} foi aceito e recebeu o cargo!", ephemeral=True)
            
            try:
                await candidato.send(f"🎉 Parabéns! Você passou na primeira parte do recrutamento em **{guild.name}**. Abra um ticket no servidor para darmos continuidade!")
            except:
                pass 

            await interaction.message.edit(view=None)
        else:
            await interaction.response.send_message("Erro: Membro ou Cargo não encontrado.", ephemeral=True)

    @discord.ui.button(label="Recusar", style=discord.ButtonStyle.danger)
    async def recusar(self, interaction: discord.Interaction, button: discord.ui.Button):
        candidato = interaction.guild.get_member(self.candidato_id)
        if candidato:
            await interaction.response.send_modal(ModalMotivoRecusa(candidato))
        else:
            await interaction.response.send_message("Candidato não está mais no servidor.", ephemeral=True)

# 3. MODAL DO FORMULÁRIO
class FormularioRecrutamento(discord.ui.Modal, title='Formulário de Recrutamento Staff'):
    p1 = discord.ui.TextInput(label="Qual seu nome e idade?", placeholder="Ex: João, 18 anos")
    p2 = discord.ui.TextInput(label="Por que quer ser Staff?", style=discord.TextStyle.paragraph)
    p3 = discord.ui.TextInput(label="Tem experiência anterior?", placeholder="Sim/Não, onde?")
    p4 = discord.ui.TextInput(label="Quanto tempo tem disponível?", placeholder="Ex: 4 horas")
    p5 = discord.ui.TextInput(label="Conhece as regras da cidade?", placeholder="Sim/Não")

    async def on_submit(self, interaction: discord.Interaction):
        canal_log = interaction.guild.get_channel(ID_CANAL_LOG)
        if not canal_log:
            return await interaction.response.send_message("Erro: Canal de log não encontrado.", ephemeral=True)
        
        embed = discord.Embed(title="📝 Novo Formulário Recebido", color=discord.Color.magenta())
        embed.add_field(name="Candidato:", value=interaction.user.mention, inline=False)
        embed.add_field(name="1. Nome/Idade", value=self.p1.value, inline=False)
        embed.add_field(name="2. Motivo", value=self.p2.value, inline=False)
        embed.add_field(name="3. Experiência", value=self.p3.value, inline=False)
        embed.add_field(name="4. Disponibilidade", value=self.p4.value, inline=False)
        embed.add_field(name="5. Regras", value=self.p5.value, inline=False)

        await canal_log.send(embed=embed, view=ViewStaff(interaction.user.id))
        await interaction.response.send_message("✅ Seu formulário foi enviado com sucesso!", ephemeral=True)

class BotaoRecrutamento(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📝 Iniciar Recrutamento", style=discord.ButtonStyle.secondary, custom_id="btn_recrut")
    async def entrar_recrutamento(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FormularioRecrutamento())

class MeuBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(BotaoRecrutamento())

bot = MeuBot()

@bot.command()
@commands.has_permissions(administrator=True)
async def postar(ctx):
    embed = discord.Embed(
        title="RAZE ROLEPLAY | RECRUTAMENTO",
        description="📌 **Requisitos:**\n• +16 anos\n• Responsabilidade\n• Regras da cidade\n\nClique no botão abaixo para iniciar seu formulário.",
        color=0xFF007F
    )
    
    # Imagem configurada corretamente aqui:
    embed.set_image(url="https://media.discordapp.net/attachments/1456593912016801916/1478539505861660734/image.png")

    await ctx.send(embed=embed, view=BotaoRecrutamento())

bot.run(TOKEN)
