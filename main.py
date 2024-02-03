import disnake
import asyncio
from bs4 import BeautifulSoup
import time
import aiohttp
from disnake.ext import commands
from tkinter import *
# from disnake.errors import LoginFailure - for new futures
TOKEN = ''
SERVER_ID = ''
CHANNEL_ID = ''


def login():
    global TOKEN
    global SERVER_ID
    global CHANNEL_ID
    TOKEN = entry_TOKEN.get()
    SERVER_ID = int(entry_SERVER_ID.get())
    CHANNEL_ID = int(entry_CHANNEL_ID.get())
    root.destroy()
    return TOKEN, SERVER_ID, CHANNEL_ID


root = Tk()
root.title('Eastendmonitor by V-Solutions')
root.geometry('600x400')
label_TOKEN = Label(root, text="TOKEN:")
label_TOKEN.grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_TOKEN = Entry(root, width=70)
entry_TOKEN.grid(row=0, column=1, padx=5, pady=5)
label_SERVER_ID = Label(root, text="SERVER ID:")
label_SERVER_ID.grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_SERVER_ID = Entry(root, width=70)
entry_SERVER_ID.grid(row=1, column=1, padx=10, pady=5)
label_CHANNEL_ID = Label(root, text="CHANNEL ID:")
label_CHANNEL_ID.grid(row=2, column=0, padx=10, pady=5, sticky="e")
entry_CHANNEL_ID = Entry(root, width=70)
entry_CHANNEL_ID.grid(row=2, column=1, padx=10, pady=5)
continue_button = Button(root, text="Continue", command=login)
continue_button.grid(row=3, columnspan=2, padx=10, pady=10)
additional_text = "To start using the bot, you need to enter your bot's token here, your Discord server's ID,\n and also the ID of the channel where messages will be sent.\n\nTo get your bot's token, you need to go to discord.com, select the Developers section, create a bot there, \nadd it to your Discord server, and then copy the TOKEN from there.\n\nTo get your server's ID, you need to enable developer mode in Discord, right-click on your server, \nand copy the SERVER ID from there.\n\nTo get the CHANNEL ID for the bot, you need to right-click on the channel and copy its ID.\n\nOnce you have obtained this information, enter it in the fields above and click CONTINUE.\n\n Please note that if you make a mistake when entering this data, the application will not function correctly."
additional_label = Label(root, text=additional_text, fg="black")
additional_label.grid(row=4, columnspan=2, pady=10)
root.mainloop()
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
    global previous_outputs
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
                await asyncio.sleep(1)
                if url not in urls:
                    continue

                #PARSING START
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
                sizer = ''
                for size in sizes:
                    if size != sizes[0]:
                        if len(size) <= 17:
                            output = output + size + ' - few' + '\n'
                            size = f'{size} - few'
                        else:
                            size = size.replace(' - powiadom o dostępności', ' - 0')
                            output = output + size + '\n'
                        sizer = sizer + size + '\n'
                #PARSING FINISH

                if url not in previous_outputs or output != previous_outputs[url]:
                    previous_outputs[url] = output
                    channel = bot.get_channel(int(CHANNEL_ID))
                    embed = disnake.Embed(
                        #description=f'**price: {price} **\n\n**sizes**: \n{sizer}',
                        url=url,
                        title=name,
                        color=disnake.Color.purple()
                    )
                    embed.set_thumbnail(url=img)
                    embed.set_footer(text="V-Solutions Beta")
                    embed.add_field(name=f"Price: {price}", value="", inline=False)
                    embed.add_field(name="Sizes:", value=f"{sizer}", inline=False)
                    await channel.send(embed=embed)
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"time: {elapsed_time:.2f} sec for {len(urls)} links.")
bot = commands.Bot(command_prefix='/', intents=intents, test_guilds=[int(SERVER_ID)])


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


@bot.slash_command(name='url_add', description='Add URL for monitoring')
async def set_url(ctx, new_url):
    global urls
    urls.append(new_url)
    await ctx.send(f'new URL: <{new_url}>')


@bot.slash_command(name='urls', description='Show all URLs that are currently being monitored')
async def urls_list(ctx):
    global urls
    output = ''
    k = 0
    if len(urls) >= 1:
        for url in urls:
            k += 1
            output = output + '\n' + f'{k}. <{url}>'
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


@bot.slash_command(name='url_remove', description='Remove one URL')
async def url_remove(ctx, url_number):
    global urls
    global previous_outputs
    url_number = int(url_number)
    url_number -= 1
    url_temp = urls[url_number]
    urls.pop(url_number)
    await ctx.send('URL removed.')
    await asyncio.sleep(3)
    previous_outputs.pop(url_temp)


bot.run(TOKEN)