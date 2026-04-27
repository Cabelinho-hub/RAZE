import discord
import os
from discord.ext import commands

# --- CONFIGURAÇÕES ---
TOKEN = os.getenv("DISCORD_TOKEN")
ID_CANAL_LOG = 1456450750241570887 
ID_CARGO_STAFF = 1411158389911715910 

# --- ETAPA 3 (Final) ---
class FormularioEtapa3(discord.ui.Modal, title='Recrutamento Raze - Parte 3/3'):
    q11 = discord.ui.TextInput(label="Amigo denunciado: como agiria?", style=discord.TextStyle.paragraph)
    q12 = discord.ui.TextInput(label="Lidar com jogador desrespeitoso?", style=discord.TextStyle.paragraph)
    q13 = discord.ui.TextInput(label="O que entende por abuso de poder?", style=discord.TextStyle.paragraph)
    q14 = discord.ui.TextInput(label="Diferencial: Por que você?", style=discord.TextStyle.paragraph)
    q15 = discord.ui.TextInput(label="Ciente que erro gera expulsão?", placeholder="Sim/Não")

    def __init__(self, dados):
        super().__init__()
        self.dados = dados

    async def on_submit(self, interaction: discord.Interaction):
        canal_log = interaction.guild.get_channel(ID_CANAL_LOG)
        embed = discord.Embed(title=f"📝 Formulário Staff: {self.dados['p1']}", color=discord.Color.magenta())
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        # Resumo das 15 perguntas no log
        embed.add_field(name="👤 Candidato", value=f"{interaction.user.mention}", inline=False)
        embed.add_field(name="1-5 (Identificação/Exp)", value=f"Nome: {self.dados['p1']}\nHoras: {self.dados['p2']}\nOrg: {self.dados['p3']}\nRegras: {self.dados['p4']}\nOnde foi: {self.dados['p5']}", inline=False)
        embed.add_field(name="6-10 (Postura/RP)", value=f"Dedicado: {self.dados['p6']}\nHierarquia: {self.dados['p7']}\nExigências: {self.dados['p8']}\nAção RP: {self.dados['p9']}\nFora Ticket: {self.dados['p10']}", inline=False)
        embed.add_field(name="11-15 (Ética/Final)", value=f"Amigo: {self.q11.value}\nPressão: {self.q12.value}\nAbuso: {self.q13.value}\nDiferencial: {self.q14.value}\nCompromisso: {self.q15.value}", inline=False)

        await canal_log.send(embed=embed, view=ViewStaff(interaction.user.id))
        await interaction.response.send_message("✅ Formulário enviado com sucesso!", ephemeral=True)

# --- ETAPA 2 ---
class FormularioEtapa2(discord.ui.Modal, title='Recrutamento Raze - Parte 2/3'):
    q6 = discord.ui.TextInput(label="Quantas horas por dia pretende dedicar?")
    q7 = discord.ui.TextInput(label="Superior errado: como você agiria?", style=discord.TextStyle.paragraph)
    q8 = discord.ui.TextInput(label="Se adequaria às exigências da staff?")
    q9 = discord.ui.TextInput(label="Denúncia em ação de RP: O que faz?", style=discord.TextStyle.paragraph)
    q10 = discord.ui.TextInput(label="Player insiste fora do ticket: Conduta?")

    def __init__(self, dados):
        super().__init__()
        self.dados = dados

    async def on_submit(self, interaction: discord.Interaction):
        self.dados.update({'p6': self.q6.value, 'p7': self.q7.value, 'p8': self.q8.value, 'p9': self.q9.value, 'p10': self.q10.value})
        await interaction.response.send_modal(FormularioEtapa3(self.dados))

# --- ETAPA 1 ---
class FormularioEtapa1(discord.ui.Modal, title='Recrutamento Raze - Parte 1/3'):
    q1 = discord.ui.TextInput(label="Nome RP e Idade")
    q2 = discord.ui.TextInput(label="Horários reais que garante presença?")
    q3 = discord.ui.TextInput(label="Função e Org atual (Líder/Membro)?")
    q4 = discord.ui.TextInput(label="Cite 2 regras e dê exemplo prático", style=discord.TextStyle.paragraph)
    q5 = discord.ui.TextInput(label="Onde já foi Staff e tempo?", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        dados = {'p1': self.q1.value, 'p2': self.q2.value, 'p3': self.q3.value, 'p4': self.q4.value, 'p5': self.q5.value}
        await interaction.response.send_modal(FormularioEtapa2(dados))

# --- LOGS E DECISÃO ---
class ModalMotivoRecusa(discord.ui.Modal, title='Motivo da Rejeição'):
    motivo = discord.ui.TextInput(label="Motivo:", style=discord.TextStyle.paragraph, required=True)
    def __init__(self, candidato): super().__init__(); self.candidato = candidato
    async def on_submit(self, interaction: discord.Interaction):
        try:
            embed_dm = discord.Embed(title="Raze Roleplay", description=f"Você foi recusado.\n**Motivo:** {self.motivo.value}", color=discord.Color.red())
            await self.candidato.send(embed=embed_dm)
            embed_log = interaction.message.embeds[0]
            embed_log.color = discord.Color.red()
            embed_log.add_field(name="🔴 Status", value=f"Recusado por {interaction.user.mention}\n**Motivo:** {self.motivo.value}")
            await interaction.message.edit(embed=embed_log, view=None)
            await interaction.response.send_message("Recusado.", ephemeral=True)
        except: await interaction.response.send_message("DM Fechada.", ephemeral=True)

class ViewStaff(discord.ui.View):
    def __init__(self, candidato_id): super().__init__(timeout=None); self.candidato_id = candidato_id
    @discord.ui.button(label="Aceitar", style=discord.ButtonStyle.success)
    async def aceitar(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild; candidato = guild.get_member(self.candidato_id); cargo = guild.get_role(ID_CARGO_STAFF)
        if candidato and cargo:
            await candidato.add_roles(cargo)
            embed_log = interaction.message.embeds[0]
            embed_log.color = discord.Color.green()
            embed_log.add_field(name="🟢 Status", value=f"Aceito por {interaction.user.mention}")
            await interaction.message.edit(embed=embed_log, view=None)
            await interaction.response.send_message(f"✅ Passou!", ephemeral=True)
        else: await interaction.response.send_message("Erro Membro/Cargo.", ephemeral=True)
    @discord.ui.button(label="Recusar", style=discord.ButtonStyle.danger)
    async def recusar(self, interaction: discord.Interaction, button: discord.ui.Button):
        candidato = interaction.guild.get_member(self.candidato_id)
        if candidato: await interaction.response.send_modal(ModalMotivoRecusa(candidato))

# --- BOT ---
class BotaoRecrutamento(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="📝 Iniciar Recrutamento", style=discord.ButtonStyle.secondary, custom_id="btn_recrut")
    async def entrar_recrutamento(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FormularioEtapa1())

class MeuBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default(); intents.members = True; intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
    async def setup_hook(self): self.add_view(BotaoRecrutamento())

bot = MeuBot()

@bot.command()
@commands.has_permissions(administrator=True)
async def postar(ctx):
    embed = discord.Embed(title="RAZE ROLEPLAY | RECRUTAMENTO", description="📌 O formulário possui **3 etapas** (15 perguntas).\nResponda com calma.", color=0xFF007F)
    embed.set_image(url="https://media.discordapp.net/attachments/1456593912016801916/1478539505861660734/image.png?ex=69eff5b8&is=69eea438&hm=ceed338fd89c0813a3ca460417c00fbeda374d28e5ffb0b1e56e88882496bfd0&=&format=webp&quality=lossless&width=1356&height=1356")
    await ctx.send(embed=embed, view=BotaoRecrutamento())

bot.run(TOKEN)
