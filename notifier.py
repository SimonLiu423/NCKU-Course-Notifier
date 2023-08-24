import asyncio
import datetime
import os

import pickledb
from discord.ext import commands

from utils.embed_builder import *
from utils.fetch_course import *
from utils.logger import *

TOKEN = os.environ['DISCORD_TOKEN']
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)

admin_chat = os.environ['ADMIN_CHAT']
general_chat = os.environ['GENERAL_CHAT']


@bot.event
async def on_ready():
    print('Notifier is now online!')


async def get_search_serials(listen_course):
    serials = {}
    for sn in listen_course.getall():
        sn = sn.split('-')
        dept, num = sn[0], str(sn[1])
        if dept not in serials:
            serials[dept] = []
        serials[dept].append(num)

    return serials


async def log_notify(course_id, course_name, user_ids):
    logger("{} {} updated!".format(course_id, course_name))
    for user_id in user_ids:
        user = await bot.fetch_user(user_id)
        logger("Notified user {}, id {}".format(user.name, user.id))


async def notifier():
    await bot.wait_until_ready()

    listened_course = {}
    fetch_count = 1
    # Load databases
    high_prior_db = pickledb.load('./data/high_prior.db', False)
    low_prior_db = pickledb.load('./data/low_prior.db', False)

    while True:
        # Load database
        listen_course = pickledb.load('./data/dept.db', False)
        high_prior_users = high_prior_db.getall()
        low_prior_users = low_prior_db.getall()

        print(fetch_count)
        fetch_count += 1

        serials = await get_search_serials(listen_course)
        if serials == {}:
            print('No course listening')
            await asyncio.sleep(1)
            continue
        listened_course, updated_courses = await update(listened_course, serials)

        # get each updated course
        for course_id in updated_courses:

            # Get embedded course data
            msg = "{} 餘額更新了".format(course_id)
            try:
                embed = embedBuilder(listened_course, course_id)
            except:
                print('course_id is None')
                print(updated_courses)
                break

            notified_users = []

            wanted = False
            # check if wanted in high priority group
            for user_id in high_prior_users:
                if high_prior_db.lexists(user_id, course_id):
                    user = await bot.fetch_user(user_id)
                    await user.send(msg, embed=embed)

                    wanted = True
                    notified_users.append(user_id)

            # continue and log if any high prior users wants the course
            if wanted:
                await log_notify(course_id, updated_courses[course_id]['cn'], notified_users)
                continue

            # low priority group
            for user_id in low_prior_users:
                if low_prior_db.lexists(user_id, course_id):
                    user = await bot.fetch_user(user_id)
                    await user.send(msg, embed=embed)
                    wanted = True

            # continue and log if wanted
            if wanted:
                await log_notify(course_id, updated_courses[course_id]['cn'], notified_users)
                continue

            # send to class dc if not wanted
            # channel = bot.get_channel(general_chat)
            channel = bot.get_channel(admin_chat)
            await channel.send(msg, embed=embed)

        await asyncio.sleep(1)


bot.loop.create_task(notifier())
bot.run(TOKEN)
