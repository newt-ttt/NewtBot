import numpy as np
import random as rd
import discord
from discord import Intents
import os
import time
from time import sleep
import asyncio
import scanning_functions
import vt
import hashlib
import pytube as pt

def embedbuilder(Title, desc, size = None, Color= None):
    results = 'Results:'
    if Color == None:
        Color = discord.Color.blue()
    if type(desc) == vt.object.WhistleBlowerDict:
        if size != None:
            results = 'Size: {}\n'.format(size)
        for key in desc.keys():
            results += '{}: {}\n'.format(str(key), desc[key])
        embed = discord.Embed(title= Title, description= results, color= Color)
    else:
        embed = discord.Embed(title= Title, description= desc, color= Color)
    return embed

def create_hash(filename):
    with open('vtfiles/{}'.format(filename), 'rb') as file:
        hash = hashlib.sha256(file.read()).hexdigest()
    return hash

vtclient = vt.Client("70c6d2530457122bd29f961514fef3b54801b8f0c0d1a916b3f1f9f92cfa92b2")

intent = discord.Intents.default()
intent.messages= True
intent.members = True
intent.guilds = True

client = discord.Client(intents = Intents.all())

class MyClient(discord.Client):
    VCqueue = []
    VCclient = None
    VCcurrent = (None, None)
    VCloop = False
    
    @client.event
    async def on_ready():
        print('We have logged in as {0.user}'.format(client))
        
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        
        #VIRUS SCANNING CODE IN FILES
        if len(message.attachments) > 0:
            #saves attachment in message, returns name of file
            fname = await scanning_functions.grab_file(message)
            file = None
            with open(f'vtfiles/{fname}', "rb") as f:
                
                size = os.stat('vtfiles/{}'.format(fname)).st_size
                
                #formatting size in kb/mb/gb, etc
                size = await scanning_functions.format_filesize(size)
                try:
                    hash = create_hash(fname)
                    scannedfile = await vtclient.get_object_async('/files/{}'.format(hash))
                    await message.channel.send(embed=embedbuilder(fname, scannedfile.last_analysis_stats, size))
                    print('Found via hash')
                    
                except:
                    await message.channel.send('File requires scanning, this could take up to a few minutes.')
                    #record time 
                    t1 = time.time()
                    #scanning file
                    file = await vtclient.scan_file_async(f, wait_for_completion=True)
                    t2 = time.time()
                    #formatting results into embed
                    await message.channel.send(embed=embedbuilder(fname, file.stats, size))
                    await message.channel.send(f'File scanned in {round(t2-t1, 2)}s')
                    print('File scanned')
                    
        # VIRUS SCANNING CODE IN URLS
        elif any([prefix in message.content for prefix in ["http://", "https://"]]):
            
            msg_url = message.content.strip().split(" ")
            for segment in msg_url:
                
                if any([prefix in segment for prefix in ["http://", "https://"]]):
                    
                    t1 = time.time()
                    #scan segment
                    segment_url_id = vt.url_id(segment)
                    
                    try:
                        url_analysis = await vtclient.get_object_async("/urls/{}", segment_url_id)
                        await message.channel.send(embed=embedbuilder(segment, url_analysis.last_analysis_stats))
                        
                    except:
                        url_analysis = await vtclient.scan_url_async(segment, wait_for_completion=True)
                        await message.channel.send(embed=embedbuilder(segment, url_analysis.stats))
                    
                    t2 = time.time()
                    await message.channel.send(f'URL scanned in {round(t2-t1, 2)}s')
            
    # MUSIC PLAYING STUFF
        if message.content.startswith('!p '):                             # Playing the first song from nothing
            
            search_req = message.content[3:]
            MyClient.VCqueue = MyClient.find_video(search_req, MyClient.VCqueue)    # Find the video and add it to the queue w/ its title

            try:
                if MyClient.VCclient.is_playing():
                    active = True
                else:
                    active = False
            except:
                    active = False
                    
            if not active: 
                
                if MyClient.VCclient is not None:
                    print("Already connected to a channel")
                else:
                    try:
                        userVC = message.author.voice               # userVC is the channel the user that sent the message is in
                        MyClient.VCclient = await userVC.channel.connect()                  # Join the channel, VCclient is a VoiceClient object
                    except AttributeError:              # If the user isnt in a channel, AttributeError is raised
                        await message.reply("User must be in a voice channel to use music commands.")
                MyClient.VCcurrent = MyClient.VCqueue.pop(0)
                current_song = discord.FFmpegPCMAudio(executable="E:\\ffmpeg\\bin\\ffmpeg.exe",source=MyClient.VCcurrent[1])   # current_song is the file at the path given as an AudioSource object
                await message.channel.send(f"Now playing: {MyClient.VCcurrent[0]}")
                
                MyClient.VCclient.play(current_song) 
                
                await MyClient.initialize_player(message)        # Begin the process for checking if we need to play the next song in queue
                
    # SKIP
        if message.content.startswith('!skip'):
            if MyClient.VCclient.is_playing() and (len(MyClient.VCqueue) != 0 or MyClient.VCloop == True):
                MyClient.VCclient.stop()
                await MyClient.playnext(message)
            else:
                MyClient.VCclient.stop()
                MyClient.VCcurrent == None
                await message.channel.send("Queue is empty, stopping.")
        
    # CLEAR
        if message.content.startswith('!clear'):
            if MyClient.VCclient.is_playing() == True:
                MyClient.VCqueue = []
                await message.channel.send("Queue has been cleared")
                
    # LOOP
        if message.content.startswith('!loop'):
            if MyClient.VCclient.is_playing() and MyClient.VCloop == False:
                MyClient.VCloop = True
                await message.channel.send("Looping On")
            else:
                MyClient.VCloop = False
                await message.channel.send("Looping Off")
    # MISC       
        if message.content.startswith("who am i"):
            await message.channel.send(str(message.author.id))
        
        if message.content.startswith("print members"):
            members = 'All Members:\n'
            async for i in message.author.guild.fetch_members():
                members += '>'+i.name + '\n'
            await message.channel.send(members)
            
            
    async def initialize_player(message):
        """_summary_
            This function basically polls whenever there's something playing, so that once it ends it automatically goes to the next item.
        Args:
            message (_type_): _description_
        """
        while True:
            if MyClient.VCclient.is_playing():
                await asyncio.sleep(0.1)
            else:
                try:
                    await MyClient.playnext(message)
                except:
                    await message.channel.send("Queue is empty, stopping.")
                    return
            
    async def playnext(message):
        if MyClient.VCloop == False:
            MyClient.VCcurrent = MyClient.VCqueue.pop(0)
            
        (current_title, current_path) = MyClient.VCcurrent
        current_song = discord.FFmpegPCMAudio(executable="E:\\ffmpeg\\bin\\ffmpeg.exe",source=current_path)
        await message.channel.send(f"Now playing: {current_title}")
        MyClient.VCclient.play(current_song)
        
    def find_video(search_param, queue):
        topresult = pt.Search(search_param).results[0]
        audio_track = topresult.streams.filter(abr=None)[-1]
        path = audio_track.download(output_path="E:\\newtbot\\queue")
        queue.append((topresult.title, path))
        print(queue)
        return queue
     
client.run("OTAwMTYzNTE2MTk4MTY2NTg4.G-0JxO.RhqoHbxyYFZ4VIfY3d_5RxKw18SezMWJzZiQCY")
