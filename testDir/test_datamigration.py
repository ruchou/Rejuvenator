import pytest
from main import Rejuvenator


class TestDataMigration:
    """
        Test Rejuvenator's Data Migration function
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
    
    
    def test_one(self):
        pass
    
    def test_two(self):
        pass
    
    def test_three(self):
        pass
    
    def test_four(self):
        pass
    
    def test_five(self):
        pass