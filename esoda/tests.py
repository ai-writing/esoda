# coding: utf-8
from django.test import TestCase
from django.conf import settings

from .youdao_query import youdao_translate_new, youdao_translate_old
import time


class YoudaoAPITestCase(TestCase):
    def setUp(self):
        self.test_cases_en = ['computer', 'copyright', 'hci', 'present method']
        self.test_cases_zh = [u'中文', u'版权']

    def test_youdao_translate_new(self):
        for word in self.test_cases_en:
            self.assertEqual(youdao_translate_new(word), youdao_translate_old(word))
            time.sleep(0.1)

        for word in self.test_cases_zh:
            self.assertEqual(youdao_translate_new(word), youdao_translate_old(word))
            time.sleep(0.1)
