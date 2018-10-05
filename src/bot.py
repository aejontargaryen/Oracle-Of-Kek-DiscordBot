import discord
import asyncio

import config
import commands
import templates
from core.database import create_db_tables, get_server_model
from helpers.cmd import *
from commands.poll_cmd import is_message_active_poll, process_poll_reaction

client = discord.Client()
prefix = config.prefix
create_db_tables() # TODO probably won't stay in this file

async def process_message(msg):
    # If message doesn't start with bot prefix, stop here
    if not (msg.content).startswith(prefix):
        return

    # Split message by spaces
    msgArr = msg.content.split()
    # Separate command and args
    cmdText = msgArr[0][len(prefix):].lower()
    args = msgArr[1:] if len(msgArr) > 1 else []

    if not (cmdText in command_names):
        return

    # TODO check somewhere for if the message is a server message or sent by a bot
    # TODO check if command was sent in a server or in DM

    # Proceed to process command

    c = get_command_instance_by_name(cmdText, client)
    if bool(c):         # Ensures c actually exists
        if not c.check_privs(msg.author):
            await client.send_typing(msg.channel)
            await client.send_message(msg.channel, "Insufficient privileges for this command.")
        else:
            await c.execute(msg, args)

@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name="Online"))
    print("Connected Successfully")

@client.event
async def on_message(msg):
    await process_message(msg)

@client.event
async def on_reaction_add(reaction, user):
    if is_message_active_poll(reaction.message):
        await process_poll_reaction(reaction, user, client)

@client.event
async def on_member_join(member):
    channels = member.server.channels
    server_model = get_server_model(member.server)

    welcome_channel = None

    # If the server has a welcome channel saved, retrieve it, and make sure
    #    it is both valid, and we have permission to send messages in it
    if server_model != None:
        if server_model.welcome_channel_id != None:
            c = member.server.get_channel(server_model.welcome_channel_id)
            if c != None:
                if c.permissions_for(member.server.me).send_messages:
                    welcome_channel = c

    # If there wasn't a saved welcome channel that could be used, select a
    #    channel arbitrarily
    if welcome_channel == None:
        for c in channels:
            if c.type == ChannelType.text:
                if c.permissions_for(member.server.me).send_messages:
                    welcome_channel = c
                    break

    if welcome_channel != None:
        await client.send_typing(c)
        await client.send_message(c, templates.welcome_message.format(username_tag=member.mention))

client.run(config.token)
