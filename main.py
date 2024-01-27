import disnake
import asyncio
from bs4 import BeautifulSoup
import time
import aiohttp
from disnake.ext import commands
TOKEN = str(input('Input your TOKEN: '))
SERVER_ID = int(input('Input your server ID: '))
CHANNEL_ID = int(input('Input your channel ID: '))
urls = []
intents = disnake.Intents.all()
previous_outputs = {}
async def fetch_data(url, headers):
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    print(response)
                    if response.status == 200:
                        return await response.text()
                    else:
                        print('Something went wrong...')
        except aiohttp.InvalidURL:
            print('Invalid URL.')
            urls.remove(url)
            break
        except aiohttp.ClientConnectorError as e:
            print(f"Error: {e}")
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
                response = await fetch_data(url, headers)
                if url not in urls:
                    continue
                ###PARSING START
                soup = BeautifulSoup(response, 'html.parser')
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
                output = f' ### [{name}]({url})\n**price: {price} **\n\n**sizes:**\n'
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
                    embed = disnake.Embed(
                        description=output,
                        color=disnake.Color.purple()
                    )
                    embed.set_thumbnail(url=img)
                    embed.set_footer(text="V-Solutions Beta")
                    await channel.send(embed=embed)
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"time: {elapsed_time:.2f} sec for {len(urls)} links.")
            await asyncio.sleep(0)
bot = commands.Bot(command_prefix=None, intents=intents, test_guilds=[SERVER_ID])
@bot.event
async def on_ready():
    await bot.loop.create_task(my_loop())
@bot.event
async def on_message(message):
    if message.channel.id == CHANNEL_ID:
        await bot.process_commands(message)
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Wrong command.")
@bot.slash_command(name='url', description='Add URL for monitoring')
async def set_url(ctx, new_url):
    global urls
    urls.append(new_url)
    await ctx.send(f'new URL: {new_url}')
@bot.slash_command(name='urls', description='Show all URLs that are currently being monitored')
async def urls_list(ctx):
    global urls
    output = ''
    if len(urls) >= 1:
        for url in urls:
            output = output + '\n' + url
        await ctx.send(f'URLs:{output}')
    else:
        await ctx.send('No monitored URLs.')
@bot.slash_command(name='urls_clear', description='Remove every URL')
async def urls_clear(ctx):
    global urls
    global previous_outputs
    urls = []
    await ctx.send('No monitored URLs anymore.')
    await asyncio.sleep(8)
    previous_outputs = {}
bot.run(TOKEN)