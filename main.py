import discord
from discord.ext import commands
import asyncio
import requests
from bs4 import BeautifulSoup
import time
TOKEN = 'MTE5MTU4NjY2NDEzNzY0MjAyNA.GTGnEm.oxGVYZYmnGziGVBvsHBfhgdhJcV4voJ-O19Zfk'
CHANNEL_ID = 1179908389195755610
urls = []
intents = discord.Intents.all()
previous_outputs = {}
async def my_loop():
    global previous_output
    while True:
        if len(urls) == 0:
            print('await 10 sec')
            await asyncio.sleep(10)
        else:
            start_time = time.time()
            for url in urls:
                name = url.replace('https://eastendshop.com/pl/', '')
                name = name.replace('-', ' ')
                name = name.upper()
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}
                response = requests.get(url, headers=headers)
                print(response)
                ###PARSING START
                soup = BeautifulSoup(response.text, 'html.parser')
                price = soup.find('span', class_='price').text
                img1 = soup.find('div', class_='product media')
                img2 = img1.find('div', class_='product-slider')
                img3 = img2.find_all('a', href=True)
                img = img3[0]['href']
                data = soup.find_all('div', class_='control')
                k = 0
                for i in data:
                    k += 1
                    if k == 2:
                        data2 = i
                sizes = [option.get_text(strip=True) for option in data2.select('select#attribute156 option')]
                output = ' ### [' + str(name) + '](' + str(url) + ')' + '\n' + ' **price:  ' + str(price) + '**\n\n**sizes:**\n'
                for size in sizes:
                    if size != sizes[0]:
                        if len(size) <= 17:
                            output = output + size + ' - few' + '\n'
                        else:
                            size = size.replace(' - powiadom o dostępności', ' - 0')
                            output = output + size + '\n'
                ###PARSING FINISH
                if url not in previous_outputs or output != previous_outputs[url]:
                    previous_outputs[url] = output
                    channel = bot.get_channel(CHANNEL_ID)
                    embed = discord.Embed(
                        description=output,
                        color=discord.Color.purple()
                    )
                    embed.set_thumbnail(url=img)
                    embed.set_footer(text="V-Solutions Beta")
                    await channel.send(embed=embed)
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"time: {elapsed_time:.2f} sec")
            await asyncio.sleep(0)
bot = commands.Bot(command_prefix='/', intents=intents)
@bot.event
async def on_ready():
    bot.loop.create_task(my_loop())
@bot.event
async def on_message(message):
    if message.channel.id == CHANNEL_ID:
        await bot.process_commands(message)
@bot.command(name='url')
async def set_url(ctx, new_url):
    global urls
    urls.append(new_url)
    await ctx.send(f'new URL: {new_url}')
@bot.command(name='urls')
async def urls_list(ctx):
    global urls
    output = ''
    if len(urls) >= 1:
        for url in urls:
            output = output + '\n' + url
        await ctx.send(f'URLs:{output}')
    else:
        await ctx.send('No monitored URLs.')
@bot.command(name='urls_clear')
async def urls_clear(ctx):
    global urls
    global previous_outputs
    previous_outputs = {}
    urls = []
    await ctx.send('No monitored URLs anymore.')
bot.run(TOKEN)