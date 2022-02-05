from django.core.management.base import BaseCommand, CommandError
from smileup.models import Bot_info
from smileup.bot import send_messages

class Command(BaseCommand):

    def handle(self, *args, **options):
        bot_info = Bot_info.objects.get(nickname="smileup_bot")
        if bot_info:
            send_messages(bot_info)
        else:
            self.stdout.write('Информация о боте SmileUp не найдена.')

