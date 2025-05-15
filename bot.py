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
        f"Generate a situational interview question using the STAR format for a Project Manager in Software/IT.\n"
        f"Focus on the skill: {skill}.\n"
        f"Only describe the Situation and Task. End with: 'What would you do?'\n"
        f"Skill description: {description}"
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
        f"Evaluate this answer based on the STAR format for the skill: {skill}.\n"
        f"Candidate's answer: {user_answer}\n"
        f"Evaluation criteria:\n"
        f"- Basic level: {basic}\n"
        f"- Strong level: {strong}\n"
        f"- Advanced level: {advanced}\n"
        f"Provide the predicted result (R), the estimated level (Basic/Strong/Advanced), and a short feedback."
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
        f"Generate a sample STAR-format answer for the skill {skill}, focusing on the Action part. Skill description: {description}"
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
        f"Provide a list of recommended books, courses, and videos to improve the skill: {skill} (for Project Managers in IT/Software)."
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
    await ctx.send("🚀 Session initialized! Ready to practice your interview skills. Type /next to get your first question.")

@bot.command()
async def next(ctx):
    user_id = ctx.author.id
    if user_id not in user_sessions:
        await ctx.send("❗ Please start a session using /start")
        return

    session = user_sessions[user_id]
    session['hint_used'] = False
    skill_row = session['skills'].iloc[session['current']]
    question = generate_star_question(skill_row)
    session['current_question'] = question
    session['current_skill'] = skill_row

    await ctx.send(f"**Question:**\n{question}")

@bot.command()
async def hint(ctx):
    user_id = ctx.author.id
    session = user_sessions.get(user_id)
    if session and 'current_skill' in session:
        if session.get('hint_used'):
            await ctx.send("ℹ️ Hint already shown for this question. Use /next to get a new one.")
            return

        skill_row = session['current_skill']
        prompt = f"Give a short tip or clue on how to answer a question related to the skill: {skill_row['Skill']}\nSkill description: {skill_row['Description']}"
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        hint_text = response.choices[0].message.content
        session['hint_used'] = True
        await ctx.send(f"💡 **Hint:**\n{hint_text}")
    else:
        await ctx.send("❗ Use /next to get a question first")

@bot.command()
async def skip(ctx):
    user_id = ctx.author.id
    if user_id in user_sessions:
        user_sessions[user_id]['current'] += 1
        await next(ctx)
    else:
        await ctx.send("❗ Please start a session using /start")

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
            await ctx.send(f"📘 **Sample Answer:**\n{sample}")
    else:
        await ctx.send("❗ Use /next to get a question first")

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
            await ctx.send(f"📚 **Recommended Resources:**\n{resources}")
    else:
        await ctx.send("❗ Use /next to get a question first")

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
            await message.channel.send(f"📊 **Feedback:**\n{eval_response}")
            session['results'].append(eval_response)
            session['current'] += 1

# === RUN ===
bot.run(DISCORD_BOT_TOKEN)
