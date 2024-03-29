from django.core.management.base import BaseCommand, CommandError
from smileup.models import Bot_info, BotUser, Post
from smileup.bot import send_messages, reply_to_sender
import telebot
from django.utils import timezone
from django.urls import reverse


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            bot_info = Bot_info.objects.get(nickname="smileup_bot")
            count_active_users = BotUser.objects.filter(dialog=BotUser.IDLE).count()
            count_not_active_users = BotUser.objects.exclude(dialog=BotUser.IDLE).count()
            count_line = BotUser.objects.filter(next_message__lte=timezone.now()).filter(dialog=BotUser.IDLE).count()
            count_new_posts = Post.objects.filter(status=Post.NEW).count()
            count_edit_posts = Post.objects.filter(status=Post.EDIT).count()

            mes_stat = f"<code>СТАТИСТИКА:</code> активных/неактивных пользователей - {count_active_users}/{count_not_active_users}, "+\
                       f"в очереди на отправку - {count_line}, "+\
                       f"новых/отредактированных записей - {count_new_posts}/{count_edit_posts}"
            if count_new_posts > 0:
                cur_quote = Post.objects.filter(status=Post.NEW).order_by("?").first()
                link = "https://arhiza.pythonanywhere.com" + reverse("admin:smileup_post_change", args=[cur_quote.pk])  # TODO hardcode is not good
                for_moder = " <a href='"+link+"'>LOOK</a>"
            else:
                for_moder = ""
            
            bot = telebot.TeleBot(bot_info.token, threaded=False)
            reply_to_sender(bot_info.id_telegram_owner, mes_stat + for_moder, bot)

            send_messages(bot_info, limit=20)
        except Bot_info.DoesNotExist:
            self.stdout.write('Информация о боте SmileUp не найдена.')

