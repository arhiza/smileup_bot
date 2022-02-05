from django.db import models
import secrets, string


def id_generator(size=10, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(secrets.choice(chars) for _ in range(size))


class BotUser(models.Model):
    IDLE = "idle"
    EXPECT_Q = "e_q"
    EXPECT_F = "say"
    STOP = "stop"
    DIALOG_CHOICES = [
        (IDLE, "бот свободен"),
        (EXPECT_Q, "бот ждет цитату"),
        (EXPECT_F, "бот ждет фидбек"),
        (STOP, "бот выключен"),
    ]
    dialog = models.CharField(
        max_length=4,
        choices=DIALOG_CHOICES,
        default=IDLE,
    )
    nick_id = models.BigIntegerField(default=0)
    nick_name  = models.CharField(max_length=200)
    sent_message = models.DateTimeField(auto_now_add=True)
    next_message = models.DateTimeField(auto_now_add=True)
    need_link = models.BooleanField(default=True) # флажок "писать ли в сообщении-цитате источник"
    user_min = models.IntegerField(default=7*60) # границы временного интервала перед следующим сообщением от бота
    user_max = models.IntegerField(default=12*60)

    # TODO классовые параметры - минимум и максимум для интервала
    # что-то еще?


class Post(models.Model):
    OK = 'OK'
    NEW = 'NEW'
    EDIT = 'ED'
    #DELETED = 'DL'
    STATUS_CHOICES = [
        (OK, 'ОК'),
        (NEW, 'Новое'),
        (EDIT, 'Отредактировано'),
    ]
    status = models.CharField(
        max_length=3,
        choices=STATUS_CHOICES,
        default=NEW,
    )
    quote = models.TextField()
    link = models.TextField()
    nick_id = models.BigIntegerField(default=0)
    code = models.CharField(max_length=10, default=id_generator())

    def __str__(self):
        return self.quote


class Bot_info(models.Model):
    #никнейм бота, название бота, токен, статус активного потока, ид_владельца
    nickname = models.CharField(max_length=200)
    name  = models.CharField(max_length=200)
    token = models.CharField(max_length=200)
    #is_run = models.BooleanField(default=False)  # активного потока не будет, бот работает на веб-хуках
    id_telegram_owner = models.BigIntegerField()

    def __str__(self):
        return "{} ({})".format(self.nickname, self.name)

