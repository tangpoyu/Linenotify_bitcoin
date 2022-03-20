from scripts import below200ma, up_and_down, below200ma_2, wake_heroku
from apscheduler.schedulers.blocking import BlockingScheduler #Blocking 改 background

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=30) #一個月一次
def below200_job():
    below200ma.notify()

@sched.scheduled_job('interval', seconds=5) #每秒一次
def below200_2_job():
    below200ma_2.notify()
     
@sched.scheduled_job('interval', minutes=5) #五分鐘一次
def up_and_down_job():
     up_and_down.notify()

@sched.scheduled_job('interval', minutes=30) #30分鐘一次
def wake_heroku_job():
     wake_heroku.notify()

sched.start() #重要記得加


