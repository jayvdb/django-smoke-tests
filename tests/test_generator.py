import unittest

from django.test import TestCase
from mock import patch
from parameterized import parameterized

from django_smoke_tests.generator import SmokeTestsGenerator
from django_smoke_tests.tests import SmokeTests


# unpack to use in decorators
SUPPORTED_HTTP_METHODS = SmokeTestsGenerator.SUPPORTED_HTTP_METHODS


class DummyStream(object):
    """
    Mimics stream for tests executed withing another tests.
    Required for catching output of such tests, to not to show it in the console.
    """

    @staticmethod
    def write(*args, **kwargs):
        pass

    @staticmethod
    def flush():
        pass


class TestSmokeTestsGenerator(TestCase):
    def setUp(self):
        super(TestSmokeTestsGenerator, self).setUp()
        self.tests_generator = SmokeTestsGenerator()

    @parameterized.expand(SUPPORTED_HTTP_METHODS)
    @patch('django_smoke_tests.tests.SmokeTests')
    def test_create_test_for_http_method(self, http_method, MockedSmokeTests):
        endpoint_name = 'simple-endpoint'
        url = '/simple-url'
        self.tests_generator.create_test_for_http_method(http_method, url, endpoint_name)

        expected_test_name = self.tests_generator.create_test_name(http_method, endpoint_name)
        self.assertTrue(
            hasattr(MockedSmokeTests, expected_test_name)
        )

    def _execute_smoke_test(self, test_name):
        """
        Executes one test inside current test suite.
        Be careful as it's kind on inception.
        """
        suite = unittest.TestSuite()
        suite.addTest(SmokeTests(test_name))
        test_runner = unittest.TextTestRunner(stream=DummyStream).run(suite)

        self.assertEqual(test_runner.errors, [])  # errors are never expected
        return test_runner.wasSuccessful(), test_runner.failures

    @parameterized.expand(SUPPORTED_HTTP_METHODS)
    def test_execute_smoke_test_that_passes(self, http_method):

        # use new endpoint to be sure that test was not created in previous tests
        endpoint_name = self.tests_generator.create_random_string(length=10)
        endpoint_url = '/{}'.format(endpoint_name)
        expected_test_name = self.tests_generator.create_test_name(http_method, endpoint_name)

        self.tests_generator.create_test_for_http_method(
            http_method, endpoint_url, endpoint_name, detail_url=True
        )  # detail_url set to True to allow 404

        # check if test was created and added to test class
        self.assertTrue(
            hasattr(SmokeTests, expected_test_name)
        )

        is_successful, failures = self._execute_smoke_test(expected_test_name)
        self.assertTrue(is_successful)
        self.assertEqual(failures, [])
