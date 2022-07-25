import pytest
from main import Rejuvenator


class TestWrite:
    """
    Test Rejuvenator's Write function
    """
    @classmethod
    def setup_class(self):
        print("set up class")

    @classmethod
    def teardown_class(self):
        print("tear down the class")

    def setup_method(self, method):
        """setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        print("set up the method")
        self.r = Rejuvenator()

    def teardown_method(self, method):
        """teardown any state that was previously setup with a setup_method
        call.
        """
        print("tear down the method")
        self.r = None

    # TODO add more unit tests to test write()
    # example
    def test_one(self):
        self.r.write(d=10, lb=1, lp=5)

        assert self.r.n_page == 100