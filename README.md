# PM-Bot
A conversational AI-powered Discord bot for practicing Project Manager interviews using the STAR method. Designed to help you train real-world thinking and answer structuring before facing hiring managers.

🔍 What It Does
PM Interview Bot simulates situational interview questions for IT/Software Project Manager roles. It:
- Loads a customizable skill matrix from a local CSV file.\-
- Asks one question at a time in the STAR format:
  - Situation
  - Task
  - Action (your part)
  - Result (GPT predicts and evaluates it)
- Uses OpenAI GPT-4o to generate questions, hints, feedback, and learning resources.
- Fully integrated with Discord via discord.py.

| Command      | Description                                                                                 |
| ------------ | ------------------------------------------------------------------------------------------- |
| `/start`     | Starts your interview simulation session.                                                   |
| `/next`      | Get a new STAR interview question.                                                          |
| `/hint`      | Shows a **short tip** to help you answer.                                                   |
| `/answer`    | Shows a **sample answer** to the current question.                                          |
| `/info`      | Recommends **books, courses, and lectures** related to the current skill.                   |
| `/skip`      | Skips the current question.                                                                 |
| `Just reply` | Type your answer — the bot will analyze it, provide feedback and estimate your skill level. |

⚙️ Tech Stack
- Python 3.10+
- discord.py
- openai (v1.x API)
- pandas
- python-dotenv
- Local CSV for skills (e.g., Skill Matrix Software PM.csv)

🛠 Installation
git clone https://github.com/martianteapot/PM-Bot.git
cd pm-interview-bot
pip install -r requirements.txt

Create a .env file:
OPENAI_API_KEY=your_openai_key
DISCORD_BOT_TOKEN=your_discord_token

Run the bot:
python bot.py

🧠 STAR Method Explained
The STAR technique is widely used in competency-based interviews:
- Situation – Describe the context.
- Task – What was your responsibility?
- Action – What did you do?
- Result – What was the outcome?

PM Interview Bot helps you master this format by providing dynamic examples and real-time feedback.

🤝 Contributing
PRs welcome! Want to adapt the bot to another role (e.g. DevOps, QA, Designer)? Fork it and tweak the CSV!
