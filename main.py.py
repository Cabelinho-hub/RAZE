import discord
from discord.ext import commands
from discord import app_commands

# --- CONFIGURAÇÕES ---
TOKEN = "SEU_TOKEN_AQUI"
ID_CANAL_LOG = 123456789  # ID do canal onde as respostas chegam para a Staff

class FormularioRecrutamento(discord.ui.Modal, title='Formulário de Recrutamento Staff'):
    # Exemplo de 3 perguntas (o limite do Discord são 5 por modal, 
    # para 10 perguntas, fazemos em duas etapas ou usamos botões)
    p1 = discord.ui.TextInput(label="Qual seu nome e idade?", placeholder="Ex: João, 18 anos", min_length=3)
    p2 = discord.ui.TextInput(label="Por que quer ser Staff?", style=discord.TextStyle.paragraph)
    p3 = discord.ui.TextInput(label="Tem experiência anterior?", placeholder="Sim/Não, onde?")
    p4 = discord.ui.TextInput(label="Quanto tempo tem disponível por dia?", placeholder="Ex: 4 horas")
    p5 = discord.ui.TextInput(label="Conhece as regras da cidade?", placeholder="Sim/Não")

    async def on_submit(self, interaction: discord.Interaction):
        canal_log = interaction.guild.get_channel(ID_CANAL_LOG)
        
        embed = discord.Embed(title="📝 Novo Formulário Recebido", color=discord.Color.magenta())
        embed.add_field(name="Candidato:", value=interaction.user.mention, inline=False)
        embed.add_field(name="1. Nome/Idade", value=self.p1.value, inline=False)
        embed.add_field(name="2. Motivo", value=self.p2.value, inline=False)
        # ... adicione os outros campos aqui ...

        # Botões de Aceitar/Recusar para a Staff
        view = discord.ui.View()
        btn_aceitar = discord.ui.Button(label="Aceitar", style=discord.ButtonStyle.success)
        btn_recusar = discord.ui.Button(label="Recusar", style=discord.ButtonStyle.danger)
        view.add_item(btn_aceitar)
        view.add_item(btn_recusar)

        await canal_log.send(embed=embed, view=view)
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
    # Aqui você pode adicionar a imagem que me mandou
    embed.set_image(url="https://media.discordapp.net/attachments/1456593884560752670/1465117968441544848/Logo_raze_roleplay_I_2048x2048_I_Jpeg.png?ex=69efe970&is=69ee97f0&hm=e31f4b16ac7e37a833bdea0da093f43f361e7a07b8f943b589089e3108d67d76&animated=true&width=1549&height=1549")
    await ctx.send(embed=embed, view=BotaoRecrutamento())

bot.run(TOKEN)
