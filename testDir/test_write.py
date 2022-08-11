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
    
    
    # write 1 time with one cold data
    def test_one_cold_data(self):
        
        #--------------------------------#
        self.r.write(d='test', lb=1, lp=5)
        #--------------------------------#
        
        # active block / page point
        assert self.r.h_clean_counter == self.r.n_phy_blocks // 2 - 1
        assert self.r.h_act_block_index_p == self.r.n_phy_blocks // 2
        assert self.r.h_act_page_p == 1
        assert self.r.l_clean_counter == self.r.n_phy_blocks // 2 - 1
        assert self.r.l_act_block_index_p == 0
        assert self.r.l_act_page_p == 0
        
        # LRU
        assert self.r.LRU[0] == (1, 5)
        for i in range(1, 100): assert self.r.LRU[i] == (None, None)
        # l2p table
        assert self.r.l_to_p[1][5] == (self.r.n_phy_blocks // 2, 0)
        # phy_page_info
        #assert self.r.phy_page_info[self.r.index_2_physical[self.r.n_phy_blocks // 2]][0] == (1, 5)
        
        
    # write 100+1 times with 101 unique cold datas
    def test_101_cold_data(self):
        
        #--------------------------------#
        for i in range(100):
            self.r.write(d=i, lb=1, lp=i)
        self.r.write(d='test', lb=2, lp=0)
        #--------------------------------#
        
        # active block / page point
        assert self.r.h_clean_counter == self.r.n_phy_blocks // 2 - 2
        assert self.r.h_act_block_index_p == self.r.n_phy_blocks // 2 + 1
        assert self.r.h_act_page_p == 1
        assert self.r.l_clean_counter == self.r.n_phy_blocks // 2 - 1
        assert self.r.l_act_block_index_p == 0
        assert self.r.l_act_page_p == 0
        
        # LRU
        for i in range(1, 99): assert self.r.LRU[i] == (1, i+1)
        assert self.r.LRU[99] == (2, 0)
        
        # l2p table
        for i in range(100): assert self.r.l_to_p[1][i] == (self.r.n_phy_blocks // 2, i)
        assert self.r.l_to_p[2][0] == (self.r.n_phy_blocks // 2 + 1, 0)
        # phy_page_info
        #for i in range(100): assert self.r.phy_page_info[self.r.index_2_physical[self.r.n_phy_blocks // 2]][i] == (1, i)
        #assert self.r.phy_page_info[self.r.index_2_physical[self.r.n_phy_blocks // 2 + 1]][0] == (2, 0)
    
    # write 2 times with one hot data
    def test_one_hot_data(self):
        
        #--------------------------------#
        self.r.write(d=1, lb=1, lp=5)
        self.r.write(d='test', lb=1, lp=5)
        #--------------------------------#
        
        # active block / page point
        assert self.r.h_clean_counter == self.r.n_phy_blocks // 2 - 1
        assert self.r.h_act_block_index_p == self.r.n_phy_blocks // 2
        assert self.r.h_act_page_p == 1
        assert self.r.l_clean_counter == self.r.n_phy_blocks // 2 - 1
        assert self.r.l_act_block_index_p == 0
        assert self.r.l_act_page_p == 1
        
        # LRU
        assert self.r.LRU[0] == (1, 5)
        for i in range(1, 100): assert self.r.LRU[i] == (None, None)
        # l2p table
        assert self.r.l_to_p[1][5] == (0, 0)
        # phy_page_info
        #assert self.r.phy_page_info[self.r.index_2_physical[self.r.n_phy_blocks // 2]][0] == 'i' # page of first write
        #assert self.r.phy_page_info[self.r.index_2_physical[0]][0] == (1, 5)                     # page of last write
        
    # write 101*2+1 times with 101 unique hot data
    def test_101_hot_data_1(self):
        
        #----------------------------------------#
        for j in range(100):
            self.r.write(d=1, lb=1, lp=j)
            self.r.write(d=2, lb=1, lp=j)
            if j==99:
                self.r.write(d='test', lb=1, lp=0)
                self.r.write(d=1, lb=2, lp=0)
                self.r.write(d=2, lb=2, lp=0)
        #----------------------------------------#
        
        # active block / page point
        assert self.r.h_clean_counter == self.r.n_phy_blocks // 2 - 2
        assert self.r.h_act_block_index_p == self.r.n_phy_blocks // 2 + 1
        assert self.r.h_act_page_p == 1
        assert self.r.l_clean_counter == self.r.n_phy_blocks // 2 - 2
        assert self.r.l_act_block_index_p == 1
        assert self.r.l_act_page_p == 2
        
        # LRU
        for i in range(2, 100): assert self.r.LRU[i-2] == (1, i)
        assert self.r.LRU[98] == (1, 0)
        assert self.r.LRU[99] == (2, 0)
        # l2p table
        assert self.r.l_to_p[1][0] == (1, 0)
        for i in range(1, 100): assert self.r.l_to_p[1][i] == (0, i)
        assert self.r.l_to_p[2][0] == (1, 1)
        # phy_page_info
        #assert self.r.phy_page_info[self.r.index_2_physical[0]][0] == 'i'
        #for i in range(1, 100): assert self.r.phy_page_info[self.r.index_2_physical[0]][i] == (1, i)
        #assert self.r.phy_page_info[self.r.index_2_physical[1]][0] == (1, 0)
        #assert self.r.phy_page_info[self.r.index_2_physical[1]][1] == (2, 0)
        #for i in range(100): assert self.r.phy_page_info[self.r.n_phy_blocks // 2][i] == 'i'
        #assert self.r.phy_page_info[self.r.index_2_physical[self.r.n_phy_blocks // 2 + 1]][0] == 'i'
        
    def _test_full_hot_data(self):
        
        #-----------------------------------------------------#
        self.r.write(d=0, lb=0, lp=0)
        for i in range(73):
            for j in range(100):
                self.r.write(d=0, lb=0, lp=0)
        #-----------------------------------------------------#
        
        assert self.r.h_clean_counter == self.r.n_phy_blocks // 2 - 1
        assert self.r.h_act_block_index_p == self.r.n_phy_blocks // 2
        assert self.r.h_act_page_p == 1
        assert self.r.l_clean_counter == 1
        assert self.r.l_act_block_index_p == self.r.n_phy_blocks // 2 - 2
        assert self.r.l_act_page_p == 0
        
        #for i in range(75):
        #    for j in range(100):
        #        if (i==73) & (j==99): assert self.r.phy_page_info[self.r.index_2_physical[i]][j] == (0, 0)
        #        elif i>73: assert self.r.phy_page_info[self.r.index_2_physical[i]][j] == 'c'
        #        else: assert self.r.phy_page_info[self.r.index_2_physical[i]][j] == 'i'
        #assert self.r.phy_page_info[self.r.n_phy_blocks // 2][0] == 'i'
        
        #---------------------------#
        for i in range(1):
            for j in range(100):
                self.r.write(d=0, lb=0, lp=0)
        #---------------------------#
        
        assert self.r.h_clean_counter == self.r.n_phy_blocks // 2 - 1
        assert self.r.h_act_block_index_p == self.r.n_phy_blocks // 2
        assert self.r.h_act_page_p == 1
        assert self.r.l_clean_counter == 1
        assert self.r.l_act_block_index_p == self.r.n_phy_blocks // 2 - 1
        assert self.r.l_act_page_p == 0
        
        # phy_page_info
        #for i in range(75):
        #    for j in range(100):
        #        if i<74: assert self.r.phy_page_info[self.r.index_2_physical[i]][j] == 'i'
        #        else: assert self.r.phy_page_info[self.r.index_2_physical[i]][j] == 'c'
        #assert self.r.phy_page_info[self.r.n_phy_blocks // 2][0] == 'i'
        #assert self.r.phy_page_info[self.r.n_phy_blocks // 2][1] == (0, 0)