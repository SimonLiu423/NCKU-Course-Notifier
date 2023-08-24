import datetime


def logger(content):
    date = datetime.datetime.now()

    path = r'./log/{}_{}_{}.log'.format(date.year, str(date.month).zfill(2), str(date.day).zfill(2))
    log_f = open(path, 'a')
    latest_f = open(r'./log/latest.log', 'a')

    current_time = datetime.datetime.now().strftime("[ {}-{}-{} %H:%M:%S ] ".format(
        date.year, str(date.month).zfill(2), str(date.day).zfill(2))
    )
    line = current_time + content + "\n"

    log_f.write(line)
    latest_f.write(line)

    log_f.close()
    latest_f.close()
