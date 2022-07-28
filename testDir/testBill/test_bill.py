import pytest
from main import Rejuvenator


class TestBillUnit:
    """
    Test helper functions in Rejuvenator
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
        self.r = Rejuvenator(n_phy_blocks=20, n_log_blocks=10, n_page=10, lru_size=5, tau=10)

    def teardown_method(self, method):
        """teardown any state that was previously setup with a setup_method
        call.
        """
        print("tear down the method")
        self.r = None

    # TODO add more unit tests to test all helper functions
    # example
    def test_one(self):
        self.r.write(d=10, lb=1, lp=5)

        assert self.r.n_page == 10

    def test_min_or_max_wear_1(self):
        self.r.n_phy_blocks = 5
        self.r.index_2_physical = [1, 2, 3, 4, 5]
        self.r.erase_count_index = [3, 4, 5]

        assert self.r.min_wear() == 0
        assert self.r.max_wear() == 2

    def test_min_or_max_wear_2(self):
        self.r.n_phy_blocks = 5
        self.r.index_2_physical = [1, 2, 3, 4, 5]
        self.r.erase_count_index = [0, 0, 5]

        assert self.r.min_wear() == 2
        assert self.r.max_wear() == 2

    def test_min_or_max_wear_3(self):
        self.r.n_phy_blocks = 5
        self.r.index_2_physical = [1, 2, 3, 4, 5]
        self.r.erase_count_index = [5, 5, 5]

        assert self.r.min_wear() == 0
        assert self.r.max_wear() == 0

    def test_get_head_1(self):
        self.r.n_phy_blocks = 5
        self.r.index_2_physical = [1, 2, 3, 4, 5]
        self.r.erase_count_index = [3, 4, 5]

        assert self.r._get_head_idx(erase_count=0) == 0
        assert self.r._get_head_idx(erase_count=1) == 3
        assert self.r._get_head_idx(erase_count=2) == 4

    def test_get_head_2(self):
        self.r.n_phy_blocks = 5
        self.r.index_2_physical = [1, 2, 3, 4, 5]
        self.r.erase_count_index = [0, 0, 5]

        assert self.r._get_head_idx(erase_count=0) == 0
        assert self.r._get_head_idx(erase_count=1) == -1
        assert self.r._get_head_idx(erase_count=2) == 0

    def test_get_head_3(self):
        self.r.n_phy_blocks = 5
        self.r.index_2_physical = [1, 2, 3, 4, 5]
        self.r.erase_count_index = [5, 5, 5]

        assert self.r._get_head_idx(erase_count=0) == 0
        assert self.r._get_head_idx(erase_count=1) == -1
        assert self.r._get_head_idx(erase_count=2) == -1

