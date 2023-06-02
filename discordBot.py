##Discord Python BOT
import os
from riotwatcher import LolWatcher, ApiError
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.guild_reactions = True
intents.dm_messages = True
intents.dm_reactions = True
intents.dm_typing = True
intents.guild_typing = True

client = discord.Client(intents=intents)

watcher = LolWatcher(os.getenv('RIOT_API_KEY'))
my_region = 'euw1'

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!register'):
        if len(message.content.split('!register ')) < 2:
            await message.channel.send('Please enter a summoner name')
            return
        if str(message.author.id) in open('data.txt').read():
            await message.channel.send('You are already registered')
            return
        open('data.txt', 'a').write(str(message.author.id) + " " + message.content.split('!register ')[1] + '\n')
        await message.channel.send('You are now registered')

    if message.content.startswith('!summoner'):
        if len(message.content.split('!summoner ')) < 2:
            await message.channel.send('Please enter a summoner name')
            return
        summonerName = message.content.split('!summoner ')[1]
        summoner = watcher.summoner.by_name(my_region, summonerName)
        await message.channel.send(f'{summonerName} is level {summoner["summonerLevel"]}')

    if message.content.startswith('!rank'):
        if len(message.content.split('!rank ')) < 2:
            await message.channel.send('Please enter a summoner name')
            return
        summonerName = message.content.split('!rank ')[1]
        summoner = watcher.summoner.by_name(my_region, summonerName)
        ranked_stats = watcher.league.by_summoner(my_region, summoner['id'])
        await message.channel.send(f'{summonerName} is {ranked_stats[0]["tier"]} {ranked_stats[0]["rank"]}')

    if message.content.startswith('!match'):
        if len(message.content.split('!match ')) < 2:
            await message.channel.send('Please enter a summoner name')
            return
        summonerName = message.content.split('!match ')[1]
        last_matches = watcher.match.matchlist_by_puuid(my_region, watcher.summoner.by_name(my_region, summonerName)['puuid'])
        last_match = last_matches[0]
        game = watcher.match.by_id(my_region, last_match)
        sumoIndex = game['metadata']['participants'].index(watcher.summoner.by_name(my_region, summonerName)['puuid'])
        champname = game['info']['participants'][sumoIndex]['championName']
        embed=discord.Embed(title=summonerName, url="https://realdrewdata.medium.com/", description="This is an embed that will show how to build an embed and the different components", color=0xFF5733)
        icon = f'http://ddragon.leagueoflegends.com/cdn/11.6.1/img/champion/{champname}.png'
        embed.set_thumbnail(url=icon)
        embed.set_author(name=champname)
        embed.add_field(name="KDA", value=str(game['info']['participants'][sumoIndex]['kills'])+"/"+str(game['info']['participants'][sumoIndex]['deaths'])+"/"+str(game['info']['participants'][sumoIndex]['assists']), inline=True)
        embed.add_field(name="Gold", value=game['info']['participants'][sumoIndex]['goldEarned'], inline=True)
        embed.add_field(name="CS", value=game['info']['participants'][sumoIndex]['totalMinionsKilled'], inline=True)
        embed.add_field(name="Vision Score", value=game['info']['participants'][sumoIndex]['visionScore'], inline=True)
        embed.add_field(name="Damage", value=game['info']['participants'][sumoIndex]['totalDamageDealtToChampions'], inline=True)
        embed.add_field(name="Damage Taken", value=game['info']['participants'][sumoIndex]['totalDamageTaken'], inline=True)

        await message.channel.send(embed=embed)

@client.event
async def on_presence_update(before,after):
    if str(before.id) in open('data.txt').read():
        if str(after.activity) == 'None':
            return
        for i,j in zip(before.activities, after.activities):
            if (i.name == "League of Legends" and j.name == "League of Legends"):
                print(str(i) + " " + str(j))
            if str(j.type) == "ActivityType.playing":
                if str(i.name) == "League of Legends" and str(j.name) == "League of Legends" and str(i.details) != str(j.details):
                    if str(i.details) == "In Queue" and str(j.details) == "Champion Select":
                        await client.get_user(before.id).send("You are now in game")
                    # if str(j.details) == "Summoner's Rift":

                    summonerName = open('data.txt').read().split(str(before.id) + ' ')[1].split('\n')[0]
                    last_matches = watcher.match.matchlist_by_puuid(my_region, watcher.summoner.by_name(my_region, summonerName)['puuid'])
                    last_match = last_matches[0]
                    game = watcher.match.by_id(my_region, last_match)
                    sumoIndex = game['metadata']['participants'].index(watcher.summoner.by_name(my_region, summonerName)['puuid'])
                    champname = game['info']['participants'][sumoIndex]['championName']
                    embed=discord.Embed(title=summonerName, url="https://realdrewdata.medium.com/", description="This is an embed that will show how to build an embed and the different components", color=0xFF5733)
                    icon = f'http://ddragon.leagueoflegends.com/cdn/11.6.1/img/champion/{champname}.png'
                    embed.set_thumbnail(url=icon)
                    embed.set_author(name=champname)
                    embed.add_field(name="KDA", value=str(game['info']['participants'][sumoIndex]['kills'])+"/"+str(game['info']['participants'][sumoIndex]['deaths'])+"/"+str(game['info']['participants'][sumoIndex]['assists']), inline=True)
                    embed.add_field(name="Gold", value=game['info']['participants'][sumoIndex]['goldEarned'], inline=True)
                    embed.add_field(name="CS", value=game['info']['participants'][sumoIndex]['totalMinionsKilled'], inline=True)
                    embed.add_field(name="Vision Score", value=game['info']['participants'][sumoIndex]['visionScore'], inline=True)
                    embed.add_field(name="Damage", value=game['info']['participants'][sumoIndex]['totalDamageDealtToChampions'], inline=True)
                    embed.add_field(name="Damage Taken", value=game['info']['participants'][sumoIndex]['totalDamageTaken'], inline=True)
                    channel = discord.utils.get(client.get_all_channels(), name='bot')
                    await channel.send(embed=embed)




client.run(TOKEN)