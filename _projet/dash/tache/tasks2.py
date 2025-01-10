# Create your tasks here

from celery import shared_task





@shared_task(bind=True)
def send_mail_fonction2(self):
    
    for i in range(10):
        print(i)

    return "done"

@shared_task
def add(x, y):
    return x*y


