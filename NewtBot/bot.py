import numpy as np
import random as rd
import discord
from discord import Intents
import os
import time
from time import sleep
import asyncio
import random
import re
import subprocess
import requests
from io import BytesIO
import vtotal
import vt
import hashlib

def embedbuilder(Title, desc, size = None, Color= None, url=None):
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
        

vtclient = vt.Client("<Insert Your VirusTotal Client Key Here>")

intent = discord.Intents.default()
intent.messages= True
intent.members = True
intent.guilds = True

client = discord.Client(intents = Intents.all())
class MyClient(discord.Client):

    @client.event
    async def on_ready():
        print('We have logged in as {0.user}'.format(client))
        
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        
        #VIRUS SCANNING CODE
        if len(message.attachments) > 0:
            #saves attachment in message, returns name of file
            fname = await vtotal.grab_file(message)
            file = None
            with open('vtfiles/{}'.format(fname), "rb") as f:
                
                #These lines do work, just are not implemented
                size = os.stat('vtfiles/{}'.format(fname)).st_size
                
                #formatting size in kb/mb/gb etc
                size = await vtotal.format_filesize(size)
                try:
                    hash = create_hash(fname)
                    scannedfile = await vtclient.get_object_async('/files/{}'.format(hash))
                    await message.channel.send(embed=embedbuilder(fname, scannedfile.last_analysis_stats, size))
                    print('hash')
                except:
                    await message.channel.send('File requires scanning, this could take up to a few minutes.')
                    #record time 
                    t1 = time.time()
                    #scanning file
                    file = await vtclient.scan_file_async(f, wait_for_completion=True)
                    t2 = time.time()
                    #formatting results into embed
                    await message.channel.send(embed=embedbuilder(fname, file.stats, size))
                    await message.channel.send('File scanned in {}s'.format(round(t2-t1, 2)))
                    print('scanned')


        if message.content.startswith('!hello'):
            await message.channel.send('Hello')
        
        if message.content.startswith("who am i"):
            await message.channel.send(str(message.author.id))
        
        if message.content.startswith("print members"):
            members = 'All Members:\n'
            async for i in message.author.guild.fetch_members():
                members += '>'+i.name + '\n'
            await message.channel.send(members)
            
        
    
        
client.run("<Insert Your Discord Key Here>")