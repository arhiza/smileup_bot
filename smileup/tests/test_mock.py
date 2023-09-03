import io
import sys
import traceback
from django.test import TestCase
from unittest.mock import Mock, patch

from smileup.bot import reply_to_sender
from smileup.models import Post, Bot_info
from smileup.management.commands.send_to_all import Command


class Redirect:
    def __init__(self, stdout = None, stderr = None) -> None:
        self.stdout = stdout
        self.old_stdout = None
        self.stderr = stderr
        self.old_stderr = None

    def __enter__(self):
        if self.stdout:
            self.old_stdout = sys.stdout
            sys.stdout = self.stdout
        if self.stderr:
            self.old_stderr = sys.stderr
            sys.stderr = self.stderr

    def __exit__(
            self,
            exc_type,
            exc_val,
            exc_tb
    ):
        if self.old_stdout:
            sys.stdout = self.old_stdout
        if exc_type:  # трейсбек исключения надо выводить в поток ошибок явно...
            sys.stderr.write(traceback.format_exc())
        if self.old_stderr:
            sys.stderr = self.old_stderr
        return True  # ...ибо при выходе из блока контекстного менеджера исключение "обнуляется"


class MockExample(TestCase):
    bot = Mock()
    bot_fail = Mock()
    bot_fail.send_message.side_effect = Exception('403 Forbidded')

    @classmethod
    def setUpTestData(cls):
        Post.objects.create(quote="TEST QUOTE", status="OK")

    def tearDown(self):
        self.bot.reset_mock()
        self.bot_fail.reset_mock()

    def test_simple_sending(self):
        stdout_test = io.StringIO()
        with Redirect(stdout=stdout_test):
            reply_to_sender(12, "Message from bot delivered", self.bot)
        self.bot.send_message.assert_called_once_with(12, 'Message from bot delivered', parse_mode='HTML')
        self.assertEqual(stdout_test.getvalue(), "")  # сообщение отправилось адресату, никаких уведомлений об ошибке
        with Redirect(stdout=stdout_test):
            reply_to_sender(67, "Message from bot not delivered", self.bot_fail)
        self.bot_fail.send_message.assert_called_once_with(67, 'Message from bot not delivered', parse_mode='HTML')
        self.assertIn("Не удалось отправить сообщение", stdout_test.getvalue())

    def test_sending_from_database(self):
        stdout_test = io.StringIO()
        with Redirect(stdout=stdout_test):
            reply_to_sender(12, "", self.bot)
        self.bot.send_message.assert_called_once_with(12, 'TEST QUOTE', parse_mode='HTML')
        self.assertEqual(stdout_test.getvalue(), "")  # сообщение отправилось адресату, никаких уведомлений об ошибке
        with Redirect(stdout=stdout_test):
            reply_to_sender(67, "", self.bot_fail)
        self.bot_fail.send_message.assert_called_once_with(67, 'TEST QUOTE', parse_mode='HTML')
        self.assertIn("Не удалось отправить сообщение", stdout_test.getvalue())


class TestManageCommand(TestCase):
    bot = Mock()
    patch_bot = patch("telebot.TeleBot", bot)

    @classmethod
    def setUpTestData(cls):
        Bot_info.objects.create(nickname="smileup_bot", token="no_token", id_telegram_owner=12345)

    def tearDown(self):
        self.bot.reset_mock()
    
    @patch_bot
    def test_empty_database(self):
        stdout_test = io.StringIO()
        with Redirect(stdout=stdout_test):
            Command().handle()
        # print(stdout_test.getvalue())
        self.assertEqual(len(self.bot.mock_calls), 3)  # создать бота; отправить в него сообщение со статистикой; создать бота для рассылки (по пустому списку пользователей, так что ничего не отправляется)
        # print(tuple(self.bot.mock_calls[1]))  # (что вызывалось, с какими позиционными параметрами, с какими именованными параметрами)
        self.assertIn("активных/неактивных пользователей - 0/0, в очереди на отправку - 0, новых/отредактированных записей - 0/0", tuple(self.bot.mock_calls[1])[1][1])
        
