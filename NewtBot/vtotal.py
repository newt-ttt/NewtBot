import vt
import asyncio

async def grab_file(message):
    files = message.attachments
    for f in files:
        fname = f.filename
        print(fname)
        #saves attachment to vtfiles directory 
        await f.save(fp='vtfiles/{}'.format(fname))
        # print message
        print('file saved successfully')
    #returns name of file
    return fname
    
async def format_filesize(size):
    if size <= 1024:
        filesize = str(size)+' b'
    elif size >= 1024:
        size//=1024
        filesize = str(size)+' kb'
    elif size//1024 >= 1024:
        size//=1024
        filesize = str(size)+' mb'
    elif size//(1024**2) >= 1024:
        size//=1024
        filesize = str(size)+' gb'
    return filesize

