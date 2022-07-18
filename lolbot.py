import discord
import requests
import tests

#discord bot token
TOKEN = ''
#riot api key
APIKey=''


client = discord.Client()

champs=tests.champs

def requestSummonerData(region,summonerName,APIKey):
   URL="https://"+region+"1.api.riotgames.com/lol/summoner/v4/summoners/by-name/"+summonerName+"?api_key="+APIKey
   response=requests.get(URL)
   return response.json()

def requestSummonerDatapuuid(region,puiid,APIKey):
    URL="https://"+region+"1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/"+puiid+"?api_key="+APIKey
    response=requests.get(URL)
    return response.json()

def requestRankedData(region,ID,APIKey):
   URL="https://"+region+"1.api.riotgames.com/lol/league/v4/entries/by-summoner/"+ID+"?api_key="+APIKey
   #print(URL)
   response=requests.get(URL)
   return response.json()

def requestChampionsData(region,ID,APIKey):
    URL="https://"+region+"1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/"+ID+"?api_key="+APIKey
    response=requests.get(URL)
    return response.json()

def requestMatchesData(region,ID,APIKey):
    if region=='euw' or 'EUW':
        region='europe'
    
    URL="https://"+region+".api.riotgames.com/lol/match/v5/matches/by-puuid/"+ID+"/ids?start=0&count=20&api_key="+APIKey
    response=requests.get(URL)
    return response.json()

def requestMatchInfo(region,MatchID,APIKey):
    if region=='euw' or 'EUW':
        region='europe'
    
    URL="https://"+region+".api.riotgames.com/lol/match/v5/matches/"+MatchID+"?api_key="+APIKey
    response=requests.get(URL)
    return response.json()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    channel=message.channel

    if message.content.startswith('rango'):
        await channel.send('¿Región?')
        msg = await client.wait_for('message')
        region=msg.content
        await channel.send('Nombre del invocador')
        msg = await client.wait_for('message')
        summonerName=msg.content
        responseJSON=requestSummonerData(region,summonerName,APIKey)
        ID=responseJSON['id']
        ID=str(ID)
        responseJSON2=requestRankedData(region,ID,APIKey)
        await channel.send(summonerName+':')
        for key in range(len(responseJSON2)):
            if str(responseJSON2[key]['queueType'])=='RANKED_FLEX_SR':
            
                await channel.send('Clasificatoria flexible: '+str(responseJSON2[key]['tier'])+' '+str(responseJSON2[key]['rank'])+' '+str(responseJSON2[key]['leaguePoints'])+'LP')
            
            else:
                await channel.send('Clasificatoria solo/dúo: '+str(responseJSON2[key]['tier'])+' '+str(responseJSON2[key]['rank'])+' '+str(responseJSON2[key]['leaguePoints'])+'LP')
        
    if message.content.startswith('campeones'):
        await channel.send('¿Región?')
        msg = await client.wait_for('message')
        region=msg.content
        await channel.send('Nombre del invocador')
        msg = await client.wait_for('message')
        summonerName=msg.content
        await channel.send('¿Cuántos campeones quieres ver?')
        msg = await client.wait_for('message')
        count=msg.content
        responseJSON=requestSummonerData(region,summonerName,APIKey)
        ID=responseJSON['id']
        ID=str(ID)
        responseJSON2=requestChampionsData(region,ID,APIKey)
        await channel.send(summonerName+':')
        for key in range(int(count)):
            await channel.send(champs[responseJSON2[key]['championId']]+' '+str(responseJSON2[key]['championPoints'])+' puntos')
    
    if message.content.startswith('historial'):
        await channel.send('¿Región?')
        msg = await client.wait_for('message')
        region=msg.content
        await channel.send('Nombre del invocador')
        msg = await client.wait_for('message')
        summonerName=msg.content
        await channel.send('¿Cuántas partidas quieres ver?')
        msg = await client.wait_for('message')
        count=msg.content
        responseJSON=requestSummonerData(region,summonerName,APIKey)
        ID=responseJSON['puuid']
        ID=str(ID)
        responseJSON2=requestMatchesData(region,ID,APIKey)
        
        for i in range(int(count)):
            responseJSON3=requestMatchInfo(region,responseJSON2[i],APIKey)
            mensaje=''
            mensaje+='---------------------------------------------------------------------\n'
            mensaje+='Partida '+str(i+1)+':\n'
            mensaje+='---------------------------------------------------------------------\n'
            mensaje+='**Equipo azul**\n'
            await channel.send(mensaje)

            azul,rojo='',''
            for t in range(5):
                summonerJSON=requestSummonerDatapuuid(region,str(responseJSON3['metadata']['participants'][t]),APIKey)
                rankJSON=requestRankedData(region,summonerJSON['id'],APIKey)
                flex,solo='Unranked','Unranked'
                for key in range(len(rankJSON)):

                    if str(rankJSON[key]['queueType'])=='RANKED_FLEX_SR':
            
                        flex='Flex: '+str(rankJSON[key]['tier'])+' '+str(rankJSON[key]['rank'])+' '+str(rankJSON[key]['leaguePoints'])+'LP'
            
                    elif str(rankJSON[key]['queueType'])=='RANKED_SOLO_5x5':
                        solo='Solo/dúo: '+str(rankJSON[key]['tier'])+' '+str(rankJSON[key]['rank'])+' '+str(rankJSON[key]['leaguePoints'])+'LP'


                azul+=responseJSON3['info']['participants'][t]['summonerName']+' | '+solo+' | || '+flex+' ||| '+responseJSON3['info']['participants'][t]['championName']+' | KDA: '+str(responseJSON3['info']['participants'][t]['kills'])+'/'\
                    +str(responseJSON3['info']['participants'][t]['deaths'])+'/'+str(responseJSON3['info']['participants'][t]['assists'])+'\n'
            
            await channel.send(azul)

            await channel.send('**Equipo rojo**')
            for t in range(5,10):
                flex,solo='Unranked','Unranked'
                summonerJSON=requestSummonerDatapuuid(region,str(responseJSON3['metadata']['participants'][t]),APIKey)
                rankJSON=requestRankedData(region,summonerJSON['id'],APIKey)
                flex,solo='Unranked','Unranked'
                for key in range(len(rankJSON)):
                    if str(rankJSON[key]['queueType'])=='RANKED_FLEX_SR':
            
                        flex='Flex: '+str(rankJSON[key]['tier'])+' '+str(rankJSON[key]['rank'])+' '+str(rankJSON[key]['leaguePoints'])+'LP'
            
                    elif str(rankJSON[key]['queueType'])=='RANKED_SOLO_5x5':
                        solo='Solo/dúo: '+str(rankJSON[key]['tier'])+' '+str(rankJSON[key]['rank'])+' '+str(rankJSON[key]['leaguePoints'])+'LP'

                rojo+=responseJSON3['info']['participants'][t]['summonerName']+' | '+solo+' | || '+flex+' ||| '+responseJSON3['info']['participants'][t]['championName']+' | KDA: '+str(responseJSON3['info']['participants'][t]['kills'])+'/'\
                    +str(responseJSON3['info']['participants'][t]['deaths'])+'/'+str(responseJSON3['info']['participants'][t]['assists'])+'\n'

            await channel.send(rojo)


client.run(TOKEN)