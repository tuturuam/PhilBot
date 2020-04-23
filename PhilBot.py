import io
import discord
import aiohttp
import discord
import logging

from PIL import Image

BOT_PREFIX = ("!")
TOKEN = 'NzAyNzMzMzQ3MTUxMDIwMTAz.XqEWWA.TCaTs2VVA-oNQIt2tA3s9e-Hb-8'

client = discord.Client()

COORDS = [(631, 551), (990, 550), (634, 308), (980, 339)]
COEFFS = [  0.6374168620866798, 0.007869343976259636, -1626.1841940303493, -0.054752838176018385, 
            0.6111123228682619, -614.03718415929, -8.243880118502314e-05, 3.514468461961497e-05]


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

def process_command(command):
    if command.author.id == client.user.id:
        return False
    try:
        if command.content.index(BOT_PREFIX) == 0:
            return command.content[1:]
    except ValueError:
        return False
    print(f'Weird command failure: {command.content}')
    return False

def process_image(buffer):
    width, height = 1219, 684
    im = Image.open(buffer).convert(mode='RGBA')
    im = im.resize((width, height), resample=Image.ANTIALIAS)
    bg = Image.open('./juan_bg.png').convert(mode='RGBA')
    im = im.transform((width * 4, height * 4), Image.PERSPECTIVE, COEFFS, Image.BICUBIC)
    im = im.resize((bg.width, bg.height), resample=Image.ANTIALIAS)

    bg = Image.alpha_composite(bg, im)

    fg = Image.open('./juan_fg.png').convert(mode='RGBA')
    bg = Image.alpha_composite(bg, fg)

    output = io.BytesIO()
    bg.save(output, format='png')
    output.seek(0)
    return output

@client.event
async def on_message(message):
    proc = process_command(message)
    if proc != False:
        command = proc.split()
        if command[0] == "philbalance":
            await message.author.send(get_user_register(message.author.id))
        if command[0] == "juan":
            # in an async function, such as an on_message handler or command
            async with aiohttp.ClientSession() as session:
                # note that it is often preferable to create a single session to use multiple times later - see below for this.
                async with session.get(command[1]) as resp:
                    buffer = io.BytesIO(await resp.read())

            await message.channel.send(file=discord.File(fp=process_image(buffer), filename="image.png"))

@client.event
async def on_reaction_add(reaction, user):
    if str(reaction).index("philcoin") >= 0:
        if reaction.message.author.id != user.id:
            add_philcoin(reaction.message.author.id, 1)


@client.event
async def on_ready():
    print('Phil Bot running')

client.run(TOKEN)
