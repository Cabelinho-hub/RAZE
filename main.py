import discord
from discord.ext import commands
import os
from flask import Flask

# --- CONFIGURAÇÃO WEB (Flask) ---
app = Flask(__name__) # Use __name__ em vez de string vazia

@app.route('/')
def home(): 
    return "Bot Online!"

# --- CONFIGURAÇÕES DO BOT ---
TOKEN = os.getenv("DISCORD_TOKEN")
ID_CANAL_LOG = 1456450750241570887 
ID_CARGO_STAFF = 1411158389911715910 

# --- CLASSES DO DISCORD (MODALS E VIEWS) ---
# (Mantenha suas classes ModalRecusa, ViewStaff, FormularioRecrutamento e BotaoInicio exatamente como estão)

class ModalRecusa(discord.ui.Modal, title='Motivo da Reprovação'):
    # ... seu código original aqui ...
    pass

class ViewStaff(discord.ui.View):
    # ... seu código original aqui ...
    pass

class FormularioRecrutamento(discord.ui.Modal, title='Recrutamento Staff'):
    # ... seu código original aqui ...
    pass

class BotaoInicio(discord.ui.View):
    # ... seu código original aqui ...
    pass

# --- BOT SETUP ---
class MeuBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(BotaoInicio())

bot = MeuBot()

@bot.command()
@commands.has_permissions(administrator=True)
async def postar(ctx):
    embed = discord.Embed(title="RAZE ROLEPLAY | RECRUTAMENTO", description="Clique no botão abaixo para iniciar.", color=0xFF007F)
    await ctx.send(embed=embed, view=BotaoInicio())

# --- INICIALIZAÇÃO ---
if __name__ == "__main__":
    # Importante: No Render, o Gunicorn chamará o 'app' e o bot rodará em paralelo
    # Para testes locais, o código abaixo funciona:
    from threading import Thread
    def run_bot():
        bot.run(TOKEN)
    
    Thread(target=run_bot).start()
    
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
