#!/usr/bin/env python
# coding: utf-8

import datetime
import os

import pickledb
from discord.ext import commands

from utils.embed_builder import *
from utils.logger import *

TOKEN = os.environ['DISCORD_TOKEN']
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)

admin_chat = os.environ['ADMIN_CHAT']
general_chat = os.environ['GENERAL_CHAT']

listen_course = pickledb.load('./data/dept.db', False)


def get_db(user_id, sync):
    if user_id in []:
        return pickledb.load('./data/high_prior.db', sync)
    else:
        return pickledb.load('./data/low_prior.db', sync)


def log_msg(ctx):
    line = "User {}, id: {} : {}".format(ctx.author, ctx.author.id, ctx.message.content)
    logger(line)


def check_id(course_id):
    if len(course_id) != 6:
        return False
    if not course_id[0].isalpha():
        return False
    if not (course_id[1].isnumeric() and course_id[3:].isnumeric()):
        return False
    if not course_id[2] == '-':
        return False
    return True


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name='add', help='add course ids to listen')
async def add(ctx):
    user_id = str(ctx.author.id)
    db = get_db(user_id, True)

    log_msg(ctx)

    ids = ctx.message.content.split(' ')[1:]

    invalid_id = []

    for course_id in ids:
        valid_id = check_id(course_id)
        if not valid_id:
            invalid_id.append(course_id)
            continue

        course_id = course_id.upper()

        if not db.exists(user_id):
            db.lcreate(user_id)

        if not db.lexists(user_id, course_id):
            db.ladd(user_id, course_id)

        if not listen_course.exists(course_id):
            listen_course.set(course_id, 1)
        else:
            listen_course.append(course_id, 1)

    db.dump()
    listen_course.dump()

    embed = discord.Embed(title="Done!", color=0x00f900)
    if not len(invalid_id) == 0:
        embed.add_field(name="Invalid ID, not added", value='\n'.join(invalid_id))
    await ctx.send(embed=embed)


@bot.command(name='list', help='list all courses added')
async def list_added(ctx):
    user_id = str(ctx.author.id)
    db = get_db(user_id, True)

    log_msg(ctx)

    if not db.exists(user_id):
        embed = discord.Embed(description="No course added", color=0xff2600)
        await ctx.send(embed=embed)
        return

    course_ids = db.lgetall(user_id)
    course_ids.sort()

    if not len(course_ids) == 0:
        embed = discord.Embed(color=0x00fdff)
        embed.add_field(name="Added course", value='\n'.join(course_ids), inline=True)
    else:
        embed = discord.Embed(description="No course added", color=0xff2600)

    await ctx.send(embed=embed)


@bot.command(name='remove', help='remove id')
async def remove(ctx):
    user_id = str(ctx.author.id)
    db = get_db(user_id, True)

    log_msg(ctx)

    ids = ctx.message.content.split(' ')[1:]

    not_added = []
    removed = []

    if ids[0] == 'all':
        removed = db.lgetall(user_id)
        db.lremlist(user_id)

        for course_id in removed:
            if listen_course.exists(course_id):
                listen_course.append(course_id, -1)
                if listen_course.get(course_id) == 0:
                    listen_course.rem(course_id)
    else:
        for course_id in ids:
            course_id = course_id.upper()

            if not db.lexists(user_id, course_id):
                not_added.append(course_id)
            else:
                db.lremvalue(user_id, course_id)
                removed.append(course_id)

                if not listen_course.exists(course_id):
                    continue

                listen_course.append(course_id, -1)
                if listen_course.get(course_id) == 0:
                    listen_course.rem(course_id)

    listen_course.dump()
    db.dump()

    # removed value for embed
    removed_embed = '\n'.join(removed)

    # not_added value for embed
    not_added_embed = '\n'.join(not_added)

    # Generate Embed
    colors = [0xff2600, 0x00f900, 0xff2600, 0xff8647]  # Red, Green, Red, Orange
    idx = (not len(removed) == 0) + 2 * (not len(not_added) == 0)

    embed = discord.Embed(color=colors[idx])
    if not len(removed) == 0:
        embed.add_field(name="Removed", value=removed_embed, inline=False)
    if not len(not_added) == 0:
        embed.add_field(name="Not added", value=not_added_embed, inline=False)

    # Send message
    await ctx.send(embed=embed)


@bot.command(name='orz', help='Orz')
async def orz(ctx):
    log_msg(ctx)

    f = open('assets/orz.gif', mode='rb')
    picture = discord.File(f)
    await ctx.send(ctx.message.content.split(' ')[1], file=picture)
    f.close()


@bot.command(name='test', help='test function')
async def test(ctx):
    log_msg(ctx)

    test_courses = {
        'Meow-030': {
            'cn': "貓咪行為學",
            'i': ["Old Deuteronomy"],
            't': ['0,1,9,a,b,c'],
            'a': -1,
        }
    }
    embed = embedBuilder(test_courses, "Meow-030")
    user = ctx.author
    await user.send("喵嗚", embed=embed)


bot.run(TOKEN)
