import telebot
import random
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from .models import Bot_info, Post, BotUser

def get_random_post(to_id):
    return Post.objects.filter(Q(nick_id=to_id) | Q(status=Post.OK)).order_by("?").first()

def reply_to_sender(sender_id, mes, bot, bot_user=None):
    if mes == "":
        post = get_random_post(sender_id)
        mes = post.quote
        if bot_user:
            if bot_user.need_link and (post.link != ""): # писать источник цитаты в скобках
                mes = mes + " (" + post.link + ")"
            bot_user.sent_message = timezone.now()
            bot_user.next_message = timezone.now() + timezone.timedelta(minutes=random.randint(bot_user.user_min, bot_user.user_max)) # случайный интервал до следующего раза
            bot_user.dialog = BotUser.IDLE
            bot_user.save()
    try:
        bot.send_message(sender_id, mes, parse_mode='HTML')
    except Exception as e:
        print("Не удалось отправить сообщение для user_id", sender_id, "\n", e)
        if bot_user:
            bot_user.dialog = BotUser.STOP
            bot_user.save()
            print("Для пользователя", bot_user.nick_name, "бот выключен")

# рассылка сообщений
def send_messages(bot_info, limit=4):
    bot = telebot.TeleBot(bot_info.token, threaded=False)
    to_users = BotUser.objects.filter(next_message__lte=timezone.now()).filter(dialog=BotUser.IDLE).order_by('next_message')[:limit]
    for bot_user in to_users:
        reply_to_sender(bot_user.nick_id, "", bot, bot_user)

# добавить цитату в базу данных, вернуть ид цитаты и пароль
def add_quote(quote, nick_id, link="", status=Post.NEW):
    post = Post.objects.create(quote=quote, link=link, nick_id=nick_id, status=status)
    return post.pk, post.code

def parse_command(text):
    if not text:
        return "", ""
    if text.startswith("/"):
        blank = text.find(" ")
        if blank>0:
            return text[:blank], text[blank+1:]
        else:
            return text, ""
    else:
        return "", text

def get_name(data_from, bot_info):
    names = ['username', 'first_name']  # TODO django.db.utils.OperationalError: (1366, "Incorrect string value: '\\xF0\\x9F\\x9A\\x80' for column 'nick_name' at row 1")
    for name in names:
        if name in data_from.keys():
            return data_from[name]
    mes_err = "<code>ТЕХНИЧЕСКОЕ:</code> неочевидное поле для обращения - "+str(data_from)
    bot = telebot.TeleBot(bot_info.token, threaded=False)
    reply_to_sender(bot_info.id_telegram_owner, mes_err, bot)
    return "Anonymous"

# парсить сообщение, полученное ботом, выполнять команду, если это она, или отправлять просто ответ из базы данных
def parse_input_message(request, data, bot_info):
    print(data)
    if 'message' not in data.keys():
        # сообщения типа таких - {'update_id': 111111111, 'my_chat_member':
        #{'chat': {'id': 3333333333, 'first_name': 'КТО-ТО', 'last_name': 'КАКОЙ-ТО', 'username': 'никнейм', 'type': 'private'},
        #'from': {'id': 3333333333, 'is_bot': False, 'first_name': 'КТО-ТО', 'last_name': 'КАКОЙ-ТО', 'username': 'никнейм', 'language_code': 'ru'},
        #'date': 1628262710, 'old_chat_member': {'user': {'id': 9999999999, 'is_bot': True, 'first_name': 'SmileUp', 'username': 'smileup_bot'},
        #'status': 'member'}, 'new_chat_member': {'user': {'id': 9999999999, 'is_bot': True, 'first_name': 'SmileUp', 'username': 'smileup_bot'},
        #'status': 'kicked', 'until_date': 0}}} - это от телеграма про то, что бота удалили
        sender_id = data['my_chat_member']['chat']['id']
        bot_user = BotUser.objects.filter(nick_id=sender_id).first()
        if bot_user:
            bot_user.dialog = BotUser.STOP
            bot_user.save()
            print("Для пользователя", bot_user.nick_name, "бот выключен")
    else:
        sender_id = data['message']['from']['id']
        sender_name = get_name(data['message']['from'], bot_info)

        #запоминаем к себе отправителя, даже если он в первый раз сумел зайти без команды "старт"
        bot_user = BotUser.objects.filter(nick_id=sender_id).first()
        if not bot_user:
            bot_user = BotUser.objects.create(nick_id=sender_id)
            try:
                bot_user.nick_name = sender_name
                bot_user.save()
            except:
                print("Не удалось сохранить ник '{}' для пользователя {}".format(sender_name, sender_id))
                bot_user.nick_name = "Anonymous"

        try:
            text = data['message']['text']
        except:
            text = None
        mes = ""
        if text or (bot_user.dialog == BotUser.EXPECT_F):
            command, text = parse_command(text)
            # выполняем команду
            if (command == "/add") or (command == "" and bot_user.dialog == BotUser.EXPECT_Q): #
                quote = text
                if len(quote)==0:
                    # следующее сообщение от этого же отправителя распознать как цитату для добавления
                    mes = "Приготовил ручку и внимательно слушаю.\nОтправьте в сообщении либо <code>цитата</code>, либо <code>цитата # источник</code>"
                    bot_user.dialog = BotUser.EXPECT_Q
                    bot_user.save()
                else:
                    quote = (quote+"#").split("#")
                    print(quote[0], quote[1])
                    status = Post.NEW
                    if bot_info.id_telegram_owner == sender_id:
                        status = Post.OK
                    rr = add_quote(quote=quote[0].strip(), nick_id=sender_id, link=quote[1].strip(), status=status)
                    link = request.build_absolute_uri(reverse('edit_quote', args=(str(rr[0]), rr[1])))
                    mes = "Hi, "+sender_name+". Цитата добавлена, можно <a href='"+link+"'>отредактировать</a>."
                    bot_user.dialog = BotUser.IDLE
                    bot_user.save()

            elif command == "/feedback" or (command == "" and bot_user.dialog == BotUser.EXPECT_F): #
                if command == "/feedback" and len(text)==0:
                    mes = "Следующее сообщение будет переслано создателю."
                    bot_user.dialog = BotUser.EXPECT_F
                    bot_user.save()
                else: # пересылается либо следующее за командой сообщение целиком, либо сразу сообщение с командой, если в нем был еще и текст
                    bot = telebot.TeleBot(bot_info.token, threaded=False)
                    bot.forward_message(bot_info.id_telegram_owner, sender_id, data['message']['message_id'])
                    mes = "Спасибо! Сообщение переслано." #str(data['message']) #
                    bot_user.dialog = BotUser.IDLE
                    bot_user.save()
                    print("Переслано сообщение от user_id", sender_id)

            elif command == "/link":
                if bot_user.need_link:
                    bot_user.need_link = False
                    bot_user.save()
                    mes = "Отображение источников цитат ВЫКЛЮЧЕНО"
                else:
                    bot_user.need_link = True
                    bot_user.save()
                    mes = "Отображение источников цитат ВКЛЮЧЕНО"

            elif command == "/stop":
                mes = "Рассылка выключена. Чтобы включить обратно, напишите что-нибудь боту."
                bot_user.dialog = BotUser.STOP
                bot_user.save()

            elif command == "/settings":
                mes = "/link - включить/выключить отображение источников цитат\n/stop - выключить рассылку"

            elif command == "/help":
                mes = "/add - добавить новую цитату (если что-то пойдет не так (опечатки и всё такое), запись можно будет отредактировать)\n/feedback - переслать сообщение хранителю бота\n/settings - настройки (включение-выключение источников цитат, выключение бота)"

            elif command in {"/start","/start@smileup_bot"}:
                mes = "Hi, "+sender_name+". Приятно познакомиться!\n\nЯ - бот! Создан, чтобы делиться цитатами из книжек. Иногда (надеюсь, что не очень часто) делаю это сам, либо отправляю что-нибудь в ответ на запрос. Если нужен знак или что-то для улучшения настроения - просто напишите мне. Если не помогло - не относитесь серьезно, я все-таки бот.\n\n\nДля пополнения запаса цитат пользуйтесь командой <code>/add</code>, либо <code>/add цитата # источник</code>, как удобнее."

            elif len(command)>0:
                mes = "Не могу разобрать команду '"+command+"'"

        print(mes)
        bot = telebot.TeleBot(bot_info.token, threaded=False)
        reply_to_sender(sender_id, mes, bot, bot_user)
    send_messages(bot_info) # и всем, кто молча ждет весточки, тоже что-нибудь поотправлять

