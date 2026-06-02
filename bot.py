import discord
from discord.ext import commands
import os
import json
import asyncio
import random
from datetime import datetime

# 🤖 디스코드 로블록스 자동 판매 봇 (Managed by AI)
# 이 코드는 Codex/ChatGPT가 지속적으로 업데이트할 수 있도록 설계되었습니다.

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# --- 데이터베이스 관리 ---
DB_FILE = 'database.json'

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "inventory": {},  # {item_name: {"price": 1000, "stock": 10, "description": ""}}
        "users": {},      # {user_id: {"balance": 0, "purchase_history": []}}
        "orders": [],     # pending orders for bank transfer verification
        "gacha": {
            "price": 500,
            "items": []   # [{"name": "item1", "rarity": "Common", "chance": 70}, ...]
        },
        "settings": {
            "admin_ids": [],
            "bank_info": "국민은행 123-456-7890 (예금주: 홍길동)",
            "backup_channel_id": None
        }
    }

def save_db(db):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

db = load_db()

# --- 관리자 체크 데코레이터 ---
def is_admin():
    async def predicate(ctx):
        return ctx.author.id in db['settings']['admin_ids'] or ctx.author.guild_permissions.administrator
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f'✅ 로그인 완료: {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="!도움말 | 로블록스 아이템 판매 중"))

# --- 기본 명령어 ---
@bot.command(name="도움말")
async def help_command(ctx):
    embed = discord.Embed(title="🚀 로블록스 자동 판매 봇 도움말", color=discord.Color.blue())
    embed.add_field(name="🛒 상점", value="!상점 - 판매 중인 아이템 목록\n!구매 [아이템명] - 아이템 구매 신청", inline=False)
    embed.add_field(name="🎰 가챠", value="!뽑기 - 랜덤 아이템 뽑기 (500원)", inline=False)
    embed.add_field(name="👤 내 정보", value="!내정보 - 잔액 및 구매 내역 확인", inline=False)
    
    if ctx.author.guild_permissions.administrator or ctx.author.id in db['settings']['admin_ids']:
        embed.add_field(name="🛠️ 관리자 전용", value="!재고추가 [이름] [가격] [수량]\n!재고수정 [이름] [수량]\n!입금확인 [유저ID] [금액]\n!공지 [내용]", inline=False)
    
    await ctx.send(embed=embed)

# --- 판매 시스템 ---
@bot.command(name="상점")
async def store(ctx):
    if not db['inventory']:
        return await ctx.send("현재 판매 중인 아이템이 없습니다.")
    
    embed = discord.Embed(title="🏪 로블록스 아이템 상점", color=discord.Color.green())
    for name, info in db['inventory'].items():
        embed.add_field(name=name, value=f"가격: {info['price']}원 | 재고: {info['stock']}개", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="구매")
async def buy(ctx, item_name: str):
    if item_name not in db['inventory']:
        return await ctx.send("존재하지 않는 아이템입니다.")
    
    item = db['inventory'][item_name]
    if item['stock'] <= 0:
        return await ctx.send("재고가 부족합니다.")
    
    user_id = str(ctx.author.id)
    user_balance = db['users'].get(user_id, {}).get('balance', 0)
    
    if user_balance >= item['price']:
        # 즉시 구매
        db['users'][user_id]['balance'] -= item['price']
        db['inventory'][item_name]['stock'] -= 1
        save_db(db)
        await ctx.send(f"✅ {item_name} 구매 완료! 잔액: {db['users'][user_id]['balance']}원\n아이템은 관리자가 곧 지급해 드릴 예정입니다.")
    else:
        # 입금 안내
        needed = item['price'] - user_balance
        await ctx.send(f"⚠️ 잔액이 부족합니다. (부족한 금액: {needed}원)\n아래 계좌로 입금 후 관리자에게 문의해 주세요.\n🏦 {db['settings']['bank_info']}")

# --- 가챠 시스템 ---
@bot.command(name="뽑기")
async def gacha(ctx):
    user_id = str(ctx.author.id)
    if db['users'].get(user_id, {}).get('balance', 0) < db['gacha']['price']:
        return await ctx.send(f"❌ 잔액이 부족합니다. (뽑기 1회: {db['gacha']['price']}원)")
    
    # 간단한 랜덤 로직 (추후 Codex가 확장 가능)
    items = ["Common 아이템", "Uncommon 아이템", "Rare 아이템", "LEGENDARY 아이템"]
    result = random.choices(items, weights=[70, 20, 9, 1])[0]
    
    db['users'][user_id]['balance'] -= db['gacha']['price']
    save_db(db)
    
    embed = discord.Embed(title="🎰 가챠 결과!", description=f"축하합니다! **[{result}]** 당첨!", color=discord.Color.gold())
    await ctx.send(embed=embed)

# --- 관리자 명령어 ---
@bot.command(name="재고추가")
@is_admin()
async def add_stock(ctx, name: str, price: int, stock: int):
    db['inventory'][name] = {"price": price, "stock": stock}
    save_db(db)
    await ctx.send(f"✅ {name} 아이템이 추가되었습니다. (가격: {price}, 재고: {stock})")

@bot.command(name="입금확인")
@is_admin()
async def verify_payment(ctx, user: discord.Member, amount: int):
    user_id = str(user.id)
    if user_id not in db['users']:
        db['users'][user_id] = {"balance": 0, "purchase_history": []}
    
    db['users'][user_id]['balance'] += amount
    save_db(db)
    await ctx.send(f"✅ {user.mention}님의 잔액에 {amount}원이 충전되었습니다. 현재 잔액: {db['users'][user_id]['balance']}원")

# --- 봇 실행 ---
token = os.getenv('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("❌ DISCORD_TOKEN 환경변수가 설정되지 않았습니다.")
