import discord
from discord.ext import commands
import pandas as pd
import openai
import random
import asyncio
import os
from dotenv import load_dotenv

# === LOAD ENV VARIABLES ===
load_dotenv()
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Load updated skill matrix
matrix = pd.read_csv('Skill Matrix Software PM.csv')

# Create the bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# === UTILITY FUNCTIONS ===
def generate_star_question(skill_row):
    skill = skill_row['Skill']
    description = skill_row.get('Description', '')
    prompt = (
        f"Згенеруй ситуаційне інтервʼю у форматі STAR для Project Manager у Software/IT.\n"
        f"Використай навичку: {skill}.\n"
        f"Опиши лише Situation і Task. Заверши фразою: 'Що ви зробите?'\n"
        f"Опис навички: {description}"
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def evaluate_answer(skill_row, user_answer):
    skill = skill_row['Skill']
    basic = skill_row.get('Level Basic', '')
    strong = skill_row.get('Level Strong', '')
    advanced = skill_row.get('Level Advanced', '')
    prompt = (
        f"Оцініть відповідь кандидата на питання за навичкою: {skill}.\n"
        f"Відповідь: {user_answer}\n"
        f"Критерії оцінки:\n"
        f"- Базовий рівень: {basic}\n"
        f"- Сильний рівень: {strong}\n"
        f"- Просунутий рівень: {advanced}\n"
        f"Зроби прогнозований результат (Result), оцінку рівня (Basic/Strong/Advanced) та короткий фідбек."
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def generate_sample_answer(skill_row):
    skill = skill_row['Skill']
    description = skill_row.get('Description', '')
    prompt = (
        f"Згенеруй приклад відповіді кандидата на питання за навичкою {skill} у форматі STAR, з акцентом на дії (Action). Опис навички: {description}"
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def generate_resources(skill_row):
    skill = skill_row['Skill']
    prompt = (
        f"Дай список рекомендованої літератури, онлайн-курсів і відеолекцій для покращення навички: {skill} (Project Management у сфері IT/Software)."
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

# === MAIN BOT LOGIC ===
user_sessions = {}

@bot.command()
async def start(ctx):
    user_id = ctx.author.id
    selected_skills = matrix.sample(10).reset_index(drop=True)
    user_sessions[user_id] = {
        'skills': selected_skills,
        'current': 0,
        'results': []
    }
    await ctx.send("🚀 Сесію ініціалізовано! Готові до практики інтерв'ю. Натисніть /next щоб отримати перше питання.")

@bot.command()
async def next(ctx):
    user_id = ctx.author.id
    if user_id not in user_sessions:
        await ctx.send("❗ Спочатку введіть /start")
        return

    session = user_sessions[user_id]
    session['hint_used'] = False
    skill_row = session['skills'].iloc[session['current']]
    question = generate_star_question(skill_row)
    session['current_question'] = question
    session['current_skill'] = skill_row

    await ctx.send(f"**Питання:**\n{question}")

@bot.command()
async def hint(ctx):
    user_id = ctx.author.id
    session = user_sessions.get(user_id)
    if session and 'current_skill' in session:
        if session.get('hint_used'):
            await ctx.send("ℹ️ Підказка на це питання вже була показана. Використай /next для нового питання.")
            return

        skill_row = session['current_skill']
        prompt = f"Дай коротку підказку або натяк, як відповісти на питання, пов'язане з навичкою: {skill_row['Skill']}\nОпис навички: {skill_row['Description']}"
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        hint_text = response.choices[0].message.content
        session['hint_used'] = True
        await ctx.send(f"💡 **Підказка:**\n{hint_text}")
    else:
        await ctx.send("❗ Спочатку введіть /next для отримання питання")

@bot.command()
async def skip(ctx):
    user_id = ctx.author.id
    if user_id in user_sessions:
        user_sessions[user_id]['current'] += 1
        await next(ctx)
    else:
        await ctx.send("❗ Спочатку введіть /start")

@bot.command()
async def answer(ctx):
    user_id = ctx.author.id
    session = user_sessions.get(user_id)
    if session and 'current_skill' in session:
        sample = generate_sample_answer(session['current_skill'])
        if len(sample) > 2000:
            for i in range(0, len(sample), 2000):
                await ctx.send(sample[i:i+2000])
        else:
            await ctx.send(f"📘 **Приклад відповіді:**\n{sample}")
    else:
        await ctx.send("❗ Спочатку введіть /next")

@bot.command()
async def info(ctx):
    user_id = ctx.author.id
    session = user_sessions.get(user_id)
    if session and 'current_skill' in session:
        resources = generate_resources(session['current_skill'])
        if len(resources) > 2000:
            for i in range(0, len(resources), 2000):
                await ctx.send(resources[i:i+2000])
        else:
            await ctx.send(f"📚 **Рекомендовані ресурси:**\n{resources}")
    else:
        await ctx.send("❗ Спочатку введіть /next")

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    user_id = message.author.id
    if user_id in user_sessions and not message.author.bot:
        session = user_sessions[user_id]
        if 'current_question' in session and not message.content.startswith('/'):
            skill_row = session['current_skill']
            user_answer = message.content
            eval_response = evaluate_answer(skill_row, user_answer)
            await message.channel.send(f"📊 **Оцінка відповіді:**\n{eval_response}")
            session['results'].append(eval_response)
            session['current'] += 1

# === RUN ===
bot.run(DISCORD_BOT_TOKEN)
