import requests
import json
import os
import discord

from dotenv import load_dotenv

from prettytable import PrettyTable

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
HELP = """ID No.     Category Name
0     Miscellaneous
1     Ammo
2     Arrows
3     Bolts
4     Construction materials
5     Construction products
6     Cooking ingredients
7     Costumes
8     Crafting materials
9     Familiars
10     Farming produce
11     Fletching materials
12     Food and Drink
13     Herblore materials
14     Hunting equipment
15     Hunting Produce
16     Jewellery
17     Mage armour
18     Mage weapons
19     Melee armour - low level
20     Melee armour - mid level
21     Melee armour - high level
22     Melee weapons - low level
23     Melee weapons - mid level
24     Melee weapons - high level
25     Mining and Smithing
26     Potions
27     Prayer armour
28     Prayer materials
29     Range armour
30     Range weapons
31     Runecrafting
32     Runes, Spells and Teleports
33     Seeds
34     Summoning scrolls
35     Tools and containers
36     Woodcutting product
37     Pocket items
38     Stone spirits
39     Salvage
40     Firemaking products
41     Archaeology materials """

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


class RuneScapeAPI:
    endpoint = 'https://secure.runescape.com/m=itemdb_rs/api/catalogue'

    # https://secure.runescape.com/m=itemdb_rs/api/catalogue/items.json?category=9&alpha=c&page=1

    index_path = "category.json"
    items_path = "items.json"
    r = requests.Session()

    def _index(self, category):
        return self.r.get(f"{self.endpoint}/{self.index_path}", params={"category": category}).json()

    def get(self, category, letter, page):
        data = []
        i = self.r.get(f"{self.endpoint}/{self.items_path}", params={"category": category, "alpha": letter, "page": page})
        try:
            results = i.json()
        except:
            return []
        for v in results["items"]:
            k = (v["name"], v["current"]["price"])
            data.append(k)
        return data

    def all(self, category):
        data = []
        for i in self._index(category)["alpha"]:
            if i["items"] > 0:
                data.extend(self.get(category, i["letter"], 1))
        return data

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def get_items(category):

    x = PrettyTable()
    api = RuneScapeAPI()
    all_items = api.all(category)

    x.field_names = ["Item", "Price"]
    for item in all_items:
        x.add_row(item)
    return f"{x}"

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("$help"):
        await message.channel.send(f"```\n{HELP}```")
    if message.content.startswith('$prices'):
        category = message.content.replace("$prices", "").strip()
        data = get_items(category)
        chunk = 1950
        if len(data) > chunk:
            for pages in list(chunks(str(data).split("\n"), 30)):
                page = "\n".join([p for p in pages])
                await message.channel.send(f"```\n{page}```")
            return
        await message.channel.send(f"```\n{data}```")





client.run(TOKEN)
