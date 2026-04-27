import discord
import os
from discord.ext import commands

# --- CONFIGURAÇÕES ---
TOKEN = os.getenv("DISCORD_TOKEN")
ID_CANAL_LOG = 1456450750241570887 
ID_CARGO_STAFF = 1411158389911715910 

# --- 1. MODAL DA ETAPA 3 (FINAL) ---
class FormularioEtapa3(discord.ui.Modal, title='Recrutamento Raze - Parte 3/3'):
    q11 = discord.ui.TextInput(label="O que faria se um amigo fosse denunciado?", style=discord.TextStyle.paragraph)
    q12 = discord.ui.TextInput(label="Como lidaria com jogador desrespeitoso?", style=discord.TextStyle.paragraph)
    q13 = discord.ui.TextInput(label="O que entende por abuso de poder?", style=discord.TextStyle.paragraph)
    q14 = discord.ui.TextInput(label="O que você pode agregar à equipe?", style=discord.TextStyle.paragraph)
    q15 = discord.ui.TextInput(label="Está ciente que descumprir regras gera remoção?", placeholder="Sim/Não. Justifique.")

    def __init__(self, dados_acumulados):
        super().__init__()
        self.dados = dados_acumulados

    async def on_submit(self, interaction: discord.Interaction):
        canal_log = interaction.guild.get_channel(ID_CANAL_LOG)
        
        embed = discord.Embed(title=f"📝 Formulário Staff: {self.dados['p1']}", color=discord.Color.magenta())
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        # Organizando as 15 respostas no Log para a Staff
        embed.add_field(name="👤 Candidato", value=f"{interaction.user.mention} (ID: `{interaction.user.id}`)", inline=False)
        embed.add_field(name="1. Nome/Idade", value=self.dados['p1'], inline=True)
        embed.add_field(name="2. Disponibilidade", value=self.dados['p2'], inline=True)
        embed.add_field(name="3. Org/Função Atual", value=self.dados['p3'], inline=False)
        embed.add_field(name="4. Regras (Prática)", value=self.dados['p4'], inline=False)
        embed.add_field(name="5. Experiência Anterior", value=self.dados['p5'], inline=False)
        
        embed.add_field(name="6. Horas Dedicadas", value=self.dados['p6'], inline=True)
        embed.add_field(name="7. Respeito à Hierarquia", value=self.dados['p7'], inline=False)
        embed.add_field(name="8. Conflito de Interesse", value=self.dados['p8'], inline=False)
        embed.add_field(name="9. Ação em Denúncia no RP", value=self.dados['p9'], inline=False)
        embed.add_field(name="10. Resolução de Conflitos", value=self.dados['p10'], inline=False)
        
        embed.add_field(name="11. Imparcialidade", value=self.q11.value, inline=False)
        embed.add_field(name="12. Controle Emocional", value=self.q12.value, inline=False)
        embed.add_field(name="13. Visão sobre Abuso", value=self.q13.value, inline=False)
        embed.add_field(name="14. Motivação/Diferencial", value=self.q14.value, inline=False)
        embed.add_field(name="15. Compromisso Final", value=self.q15.value, inline=False)

        await canal_log.send(embed=embed, view=ViewStaff(interaction.user.id))
        await interaction.response.send_message("✅ Formulário enviado com sucesso nas 3 etapas!", ephemeral=True)

# --- 2. MODAL DA ETAPA 2 ---
class FormularioEtapa2(discord.ui.Modal, title='Recrutamento Raze - Parte 2/3'):
    q6 = discord.ui.TextInput(label="Quantas horas pretende dedicar por dia?", placeholder="Ex: 5 horas")
    q7 = discord.ui.TextInput(label="Como agiria se um superior estivesse errado?", style=discord.TextStyle.paragraph)
    q8 = discord.ui.TextInput(label="Se adequaria às exigências da staff?", placeholder="Sim/Não. Justifique.")
    q9 = discord.ui.TextInput(label="Denúncia durante ação de RP: O que faz?", style=discord.TextStyle.paragraph)
    q10 = discord.ui.TextInput(label="Jogador insiste fora do ticket: Conduta?", style=discord.TextStyle.paragraph)

    def __init__(self, dados_acumulados):
        super().__init__()
        self.dados = dados_acumulados

    async def on_submit(self, interaction: discord.Interaction):
        self.dados.update({
            'p6': self.q6.value, 'p7': self.q7.value, 'p8': self.q8.value,
            'p9': self.q9.value, 'p10': self.q10.value
        })
        await interaction.response.send_modal(FormularioEtapa3(self.dados))

# --- 3. MODAL DA ETAPA 1 ---
class FormularioEtapa1(discord.ui.Modal, title='Recrutamento Raze - Parte 1/3'):
    q1 = discord.ui.TextInput(label="Nome RP e Idade (Justifique se <16)", placeholder="Ex: João Nárnia, 20 anos")
    q2 = discord.ui.TextInput(label="Horários reais que garante presença?", placeholder="Ex: 18h às 00h")
    q3 = discord.ui.TextInput(label="Função e Org atual (Líder/Membro)?", placeholder="Ex: Membro da Mecânica")
    q4 = discord.ui.TextInput(label="Cite 2 regras e dê um exemplo prático", style=discord.TextStyle.paragraph)
    q5 = discord.ui.TextInput(label="Onde já foi Staff e por quanto tempo?", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        dados = {
            'p1': self.q1.value, 'p2': self.q2.value, 'p3': self.q3.value,
            'p4': self.q4.value, 'p5': self.q5.value
        }
        await interaction.response.send_modal(FormularioEtapa2(dados))

# --- 4. SISTEMA DE LOGS E DECISÃO STAFF ---
class ModalMotivoRecusa(discord.ui.Modal, title='Motivo da Rejeição'):
    motivo = discord.ui.TextInput(label="Motivo:", style=discord.TextStyle.paragraph, required=True)
    def __init__(self, candidato):
        super().__init__(); self.candidato = candidato
    async def on_submit(self, interaction: discord.Interaction):
        try:
            embed_dm = discord.Embed(title="Recrutamento Raze", description=f"Você foi recusado.\n**Motivo:** {self.motivo.value}", color=discord.Color.red())
            await self.candidato.send(embed=embed_dm)
            embed_log = interaction.message.embeds[0]
            embed_log.color = discord.Color.red()
            embed_log.add_field(name="🔴 Status", value=f"Recusado por {interaction.user.mention}\n**Motivo:** {self.motivo.value}")
            await interaction.message.edit(embed=embed_log, view=None)
            await interaction.response.send_message("Recusado.", ephemeral=True)
        except: await interaction.response.send_message("DM Fechada.", ephemeral=True)

class ViewStaff(discord.ui.View):
    def __init__(self, candidato_id):
        super().__init__(timeout=None); self.candidato_id = candidato_id
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
            try: await candidato.send(f"🎉 Parabéns! Você passou na Staff de **{guild.name}**!")
            except: pass
        else: await interaction.response.send_message("Erro Membro/Cargo.", ephemeral=True)
    @discord.ui.button(label="Recusar", style=discord.ButtonStyle.danger)
    async def recusar(self, interaction: discord.Interaction, button: discord.ui.Button):
        candidato = interaction.guild.get_member(self.candidato_id)
        if candidato: await interaction.response.send_modal(ModalMotivoRecusa(candidato))

# --- INICIALIZAÇÃO DO BOT ---
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
    embed = discord.Embed(
        title="RAZE ROLEPLAY | RECRUTAMENTO",
        description="📌 **Requisitos:**\n• +16 anos\n• Responsabilidade\n• Regras da cidade\n\nClique no botão abaixo para iniciar seu formulário.",
        color=0xFF007F
    )
    
    # Imagem configurada corretamente aqui:
    embed.set_image(url="https://media.discordapp.net/attachments/1456593912016801916/1478539505861660734/image.png")

bot.run(TOKEN)
