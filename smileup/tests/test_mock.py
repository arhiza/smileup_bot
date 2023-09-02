import io
import sys
from django.test import TestCase
from unittest.mock import MagicMock, Mock

from smileup.bot import reply_to_sender
from smileup.models import Post


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

    def test_simple_sending(self):
        #reply_to_sender(12345, "", self.bot)
        #reply_to_sender(67890, "", self.bot_fail)
        stdout_test = io.StringIO()
        with Redirect(stdout=stdout_test):
            reply_to_sender(12, "Message from bot delivered", self.bot)
        self.bot.send_message.assert_called_once_with(12, 'Message from bot delivered', parse_mode='HTML')
        self.bot.reset_mock()  # TODO tear_down
        self.assertEqual(stdout_test.getvalue(), "")  # сообщение отправилось адресату, никаких уведомлений об ошибке

        with Redirect(stdout=stdout_test):
            reply_to_sender(67, "Message from bot not delivered", self.bot_fail)
        self.bot_fail.send_message.assert_called_once_with(67, 'Message from bot not delivered', parse_mode='HTML')
        self.bot_fail.reset_mock()  # TODO tear_down
        self.assertIn("Не удалось отправить сообщение", stdout_test.getvalue())
        
