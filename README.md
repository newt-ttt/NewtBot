# NewtBot
A WIP bot designed for server moderation, currently able to scan messages for sketchy links and attachments for viruses, and send results accordingly.

Currently the only unique functions are to scan messages and their attachments for URLs and viruses and send results.
The goal is ultimately to create a well rounded moderation tool for not just my own servers.

6/20/23
Added music player functionality with !p, !skip, !clear

-----------------------------------------------------------------------------------------------------------------------------------
bot.py contains almost all the significant code for the bot to work, and is also the main file.
scanning_functions.py includes 2 functions, one async function that downloads the file so it can be scanned, the other to format the file size into something more legible.

- Alex
