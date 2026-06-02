import discord

from discord.ext import commands

import os



# 🤖 디스코드 자동 판매 봇 베이스 코드

# 이 코드는 Codex에 의해 지속적으로 업데이트될 예정입니다.



intents = discord.Intents.default()

intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)



@bot.event

async def on_ready():
  
    print(f'✅ 로그인 완료: {bot.user.name}')
  
    await bot.change_presence(activity=discord.Game(name="자동 판매 시스템 가동 중"))
  


@bot.command()

async def 안녕(ctx):
  
    await ctx.send('안녕하세요! 자동 판매 봇입니다. 무엇을 도와드릴까요?')
  


# 토큰 설정 (Railway 환경변수 사용 권장)

token = os.getenv('DISCORD_TOKEN')

if token:
  
    bot.run(token)
  
else:
  
    print("❌ DISCORD_TOKEN 환경변수가 설정되지 않았습니다.")
  











