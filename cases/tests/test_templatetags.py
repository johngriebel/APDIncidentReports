from django.test import TestCase
from cases.templatetags.build_prefix import build_prefix


class BuildPrefix(TestCase):
    def test_build_prefix(self):
        result = build_prefix(value="foo",
                              arg="5")
        self.assertEqual("foo-5-", result)
