import discord


def embedBuilder(updated_course, course_id):
    course_name, course_teacher, course_time, course_remaining = list(updated_course[course_id].values())
    course_time = [s.split(',')[:3] for s in course_time]
    course_time = [str('[{}]{}'.format(s[0], s[1]) + ['~{}'.format(s[2]), ''][s[2] == '']) for s in course_time]
    embed = discord.Embed(title=course_id, url='https://course.ncku.edu.tw/index.php', description=course_name,
                          color=0xffe599)
    embed.add_field(name='教師', value='\n'.join(course_teacher), inline=True)
    embed.add_field(name='上課時間', value='\n'.join(course_time), inline=True)
    embed.add_field(name='\u200B', value='\u200B')
    embed.add_field(name='餘額', value=course_remaining, inline=False)
    return embed
