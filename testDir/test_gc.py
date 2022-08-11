import pytest
from main import Rejuvenator


class TestGC:
    """
        Test Rejuvenator's GC function
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
    
    def test_all_cold_data(self):
        
        #------------27 times GC------------#   # First time use all logical address
        for i in range(73+27):
            for j in range(100):
                self.r.write(d=0, lb=i, lp=j)
        #------------Start check------------#
        # parameter
        assert self.r.l_clean_counter == 47
        assert self.r.l_act_block_index_p == 27
        assert self.r.l_act_page_p == 0
        assert self.r.h_clean_counter == 1
        assert self.r.h_act_block_index_p == 148
        assert self.r.h_act_page_p == 0
        # clean
        for i in range(150):
            if i==27: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif i==148: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif (0<=i) & (i<=26): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif (75<=i) & (i<=147): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            else: assert self.r.clean[self.r.index_2_physical[i]] == True
        # is_valid_page
        for i in range(150):
            for j in range(100):
                if (0<=i) & (i<=26): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                elif (75<=i) & (i<=147): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                else: assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == False
        # erase_count_index
        for i in range(150):
            if i<13: assert self.r.erase_count_index[i] == 148
            elif i<14: assert self.r.erase_count_index[i] == 149
            else: assert self.r.erase_count_index[i] == 150
        # index_2_physical
        for i in range(150):
            if i==148: assert self.r.index_2_physical[i] == 149
            elif i==149: assert self.r.index_2_physical[i] == 148
            else: assert self.r.index_2_physical[i] == i
        #-------------End check-------------#
        
        #------------54 times GC------------#   # Keep writing cold data which is not in high # block list
        for i in range(27):                     # to maintain that there is no any invalid data in high # block list
            for j in range(100):
                self.r.write(d=0, lb=73+i, lp=j)
        #------------Start check------------#
        # parameter
        assert self.r.l_clean_counter == 20
        assert self.r.l_act_block_index_p == 40
        assert self.r.l_act_page_p == 0
        assert self.r.h_clean_counter == 1
        assert self.r.h_act_block_index_p == 54
        assert self.r.h_act_page_p == 0
        # clean
        for i in range(150):
            if i==40: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif i==54: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif (0<=i) & (i<=53): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif (75<=i) & (i<=145): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif (147<=i) & (i<=149): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            else: assert self.r.clean[self.r.index_2_physical[i]] == True
        # is_valid_page
        for i in range(150):
            for j in range(100):
                if (27<=i) & (i<=39): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                elif (41<=i) & (i<=53): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                elif (75<=i) & (i<=145): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                elif (147<=i) & (i<=149): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                else: assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == False
        # erase_count_index
        for i in range(150):
            if i<7: assert self.r.erase_count_index[i] == 146
            elif i<20: assert self.r.erase_count_index[i] == 148
            else: assert self.r.erase_count_index[i] == 150
        # index_2_physical
        for i in range(150):
            if i==148: assert self.r.index_2_physical[i] == 149
            elif i==149: assert self.r.index_2_physical[i] == 148
            else: assert self.r.index_2_physical[i] == i
        #-------------End check-------------#
        
        #------------74 times GC------------#   # Run out of low # block
        for i in range(20):                     # Check we can find & let a block in low # block list to become h_act_block_index_p
            for j in range(100):                # Holding that we can keep write although there is no clean block in high # block list
                self.r.write(d=0, lb=73+i, lp=j)
        #------------Start check------------#
        # parameter
        assert self.r.l_clean_counter == 0
        assert self.r.l_act_block_index_p == 40
        assert self.r.l_act_page_p == 0
        assert self.r.h_clean_counter == 1
        assert self.r.h_act_block_index_p == 74
        assert self.r.h_act_page_p == 0
        # clean
        for i in range(150):
            if i==40: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif i==74: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif (0<=i) & (i<=73): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif (75<=i) & (i<=145): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif (147<=i) & (i<=149): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            else: assert self.r.clean[self.r.index_2_physical[i]] == True
        # is_valid_page
        for i in range(150):
            for j in range(100):
                if (47<=i) & (i<=73): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                elif (75<=i) & (i<=145): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                elif (147<=i) & (i<=148): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                else: assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == False
        # erase_count_index
        for i in range(150):
            if i<17: assert self.r.erase_count_index[i] == 146
            elif i<20: assert self.r.erase_count_index[i] == 148
            else: assert self.r.erase_count_index[i] == 150
        # index_2_physical
        for i in range(150):
            if i==148: assert self.r.index_2_physical[i] == 149
            elif i==149: assert self.r.index_2_physical[i] == 148
            else: assert self.r.index_2_physical[i] == i
        #-------------End check-------------#
        
        #------------75~120times GC------------#    # 
        for l in range(46):                         # In this time, each coid data we write will occure GC once because l_clean_counter < 1
            self.r.write(d=0, lb=73+20, lp=l)
        #------------Start check------------#
            # parameter
            assert self.r.l_clean_counter == 0
            assert self.r.l_act_block_index_p == 40
            assert self.r.l_act_page_p == 0
            assert self.r.h_clean_counter == l+2
            assert self.r.h_act_block_index_p == 74
            assert self.r.h_act_page_p == l+1
            # clean
            for i in range(150):
                if i==40: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
                elif i==74: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
                elif (0<=i) & (i<=73): assert self.r.clean[self.r.index_2_physical[i]] == False # data
                elif (75<=i) & (i<=144-l): assert self.r.clean[self.r.index_2_physical[i]] == False # data
                elif (147<=i) & (i<=149): assert self.r.clean[self.r.index_2_physical[i]] == False # data
                else: assert self.r.clean[self.r.index_2_physical[i]] == True
            # erase_count_index
            for i in range(150):
                if i<1: assert self.r.erase_count_index[i] == 145-l
                elif i<17: assert self.r.erase_count_index[i] == 146
                elif i<20: assert self.r.erase_count_index[i] == 148
                else: assert self.r.erase_count_index[i] == 150
            # index_2_physical
            for i in range(150):
                if l<6:
                    if (46-l<=i) & (i<=46): assert self.r.index_2_physical[i] == 100+i-1
                    elif (145-l<=i) & (i<=145): assert self.r.index_2_physical[i] == i-100+1
                    elif i==148: assert self.r.index_2_physical[i] == 149
                    elif i==149: assert self.r.index_2_physical[i] == 148
                    else : assert self.r.index_2_physical[i] == i
                else:
                    if (45-l<=i) & (i<40): assert self.r.index_2_physical[i] == 100+i
                    elif (41<=i) & (i<=46): assert self.r.index_2_physical[i] == 100+i-1
                    elif (145-l<=i) & (i<140): assert self.r.index_2_physical[i] == i-100
                    elif (140<=i) & (i<=145): assert self.r.index_2_physical[i] == i-100+1
                    elif i==148: assert self.r.index_2_physical[i] == 149
                    elif i==149: assert self.r.index_2_physical[i] == 148
                    else: assert self.r.index_2_physical[i] == i
        #-------------End check-------------#
        
        #------------121~145times GC------------#   # In these write, all low # block will contain valid data
        self.r.write(d=0, lb=73+20, lp=46)          # but still no clean block in low # block list
        for i in range(6):
            self.r.write(d=0, lb=73+21+i, lp=0)
        for i in range(18):
            self.r.write(d=0, lb=73+i, lp=0)
        #------------Start check------------#
        # parameter
        assert self.r.l_clean_counter == 0
        assert self.r.l_act_block_index_p == 40
        assert self.r.l_act_page_p == 0
        assert self.r.h_clean_counter == 47
        assert self.r.h_act_block_index_p == 76
        assert self.r.h_act_page_p == 0
        # clean
        for i in range(150):
            if i==40: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif i==76: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif (0<=i) & (i<=74): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif (77<=i) & (i<=100): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif (147<=i) & (i<=149): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            else: assert self.r.clean[self.r.index_2_physical[i]] == True
        # is_valid_page
        for i in range(150):
            for j in range(100):
                if (0<=i) & (i<=39): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                elif (41<=i) & (i<=74): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                elif (77<=i) & (i<=100): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                elif (147<=i) & (i<=148): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                else: assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == False
        # erase_count_index
        for i in range(150):
            if i<1: assert self.r.erase_count_index[i] == 75
            elif i<17: assert self.r.erase_count_index[i] == 146
            elif i<20: assert self.r.erase_count_index[i] == 148
            else: assert self.r.erase_count_index[i] == 150
        # index_2_physical
        for i in range(150):
            if (0<=i) & (i<=39): assert self.r.index_2_physical[i] == 100+i
            elif (41<=i) & (i<=46): assert self.r.index_2_physical[i] == 100+i-1
            elif (47<=i) & (i<=71): assert self.r.index_2_physical[i] == 99-i+47
            elif (75<=i) & (i<=99): assert self.r.index_2_physical[i] == 99-i+47
            elif (100<=i) & (i<=139): assert self.r.index_2_physical[i] == i-100
            elif (140<=i) & (i<=145): assert self.r.index_2_physical[i] == i-100+1
            elif i==148: assert self.r.index_2_physical[i] == 149
            elif i==149: assert self.r.index_2_physical[i] == 148
            else: assert self.r.index_2_physical[i] == i
        #-------------End check-------------#
        
        #------------146times GC------------#   # erase_count_index[0] = 74 because 75th~150th blocks are erased before
        self.r.write(d=0, lb=73+18, lp=0)       # After gc, victim block (in low # block) and 74th block will be swapped
        #------------Start check------------#   # Because these two blocks are both low # block, there is a clean block in low # block list
        # parameter
        assert self.r.l_clean_counter == 1
        assert self.r.l_act_block_index_p == 40
        assert self.r.l_act_page_p == 0
        assert self.r.h_clean_counter == 46
        assert self.r.h_act_block_index_p == 75
        assert self.r.h_act_page_p == 0
        # clean
        for i in range(150):
            if i==40: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif i==75: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif (0<=i) & (i<=73): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif (76<=i) & (i<=100): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif (147<=i) & (i<=149): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            else: assert self.r.clean[self.r.index_2_physical[i]] == True
        # is_valid_page
        for i in range(150):
            for j in range(100):
                if (0<=i) & (i<=39): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                elif (41<=i) & (i<=73): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                elif (76<=i) & (i<=100): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                elif (147<=i) & (i<=148): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                else: assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == False
        # erase_count_index
        for i in range(150):
            if i<1: assert self.r.erase_count_index[i] == 74
            elif i<17: assert self.r.erase_count_index[i] == 146
            elif i<20: assert self.r.erase_count_index[i] == 148
            else: assert self.r.erase_count_index[i] == 150
        # index_2_physical
        for i in range(150):
            if (0<=i) & (i<=39): assert self.r.index_2_physical[i] == 100+i
            elif (41<=i) & (i<=46): assert self.r.index_2_physical[i] == 100+i-1
            elif (47<=i) & (i<=71): assert self.r.index_2_physical[i] == 99-i+47
            elif i==72: assert self.r.index_2_physical[i] == 74
            elif i==74: assert self.r.index_2_physical[i] == 72
            elif (75<=i) & (i<=99): assert self.r.index_2_physical[i] == 99-i+47
            elif (100<=i) & (i<=139): assert self.r.index_2_physical[i] == i-100
            elif (140<=i) & (i<=145): assert self.r.index_2_physical[i] == i-100+1
            elif i==148: assert self.r.index_2_physical[i] == 149
            elif i==149: assert self.r.index_2_physical[i] == 148
            else: assert self.r.index_2_physical[i] == i
        #-------------End check-------------#
        
        
        #-----------------------------------#
        for j in range(100):
            self.r.write(d=0, lb=73+19, lp=j)
        #------------Start check------------#
        # parameter
        assert self.r.l_clean_counter == 1
        assert self.r.l_act_block_index_p == 40
        assert self.r.l_act_page_p == 0
        assert self.r.h_clean_counter == 45
        assert self.r.h_act_block_index_p == 101
        assert self.r.h_act_page_p == 0
        # clean
        for i in range(150):
            if i==40: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif i==101: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif (0<=i) & (i<=73): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif (75<=i) & (i<=100): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif (147<=i) & (i<=149): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            else: assert self.r.clean[self.r.index_2_physical[i]] == True
        # is_valid_page
        for i in range(150):
            for j in range(100):
                if (0<=i) & (i<=39): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                elif (41<=i) & (i<=72): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                elif (75<=i) & (i<=100): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                elif (147<=i) & (i<=148): assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == True
                else: assert self.r.is_valid_page[self.r.index_2_physical[i]][j] == False
        # erase_count_index
        for i in range(150):
            if i<1: assert self.r.erase_count_index[i] == 74
            elif i<17: assert self.r.erase_count_index[i] == 146
            elif i<20: assert self.r.erase_count_index[i] == 148
            else: assert self.r.erase_count_index[i] == 150
        # index_2_physical
        for i in range(150):
            if (0<=i) & (i<=39): assert self.r.index_2_physical[i] == 100+i
            elif (41<=i) & (i<=46): assert self.r.index_2_physical[i] == 100+i-1
            elif (47<=i) & (i<=71): assert self.r.index_2_physical[i] == 99-i+47
            elif i==72: assert self.r.index_2_physical[i] == 74
            elif i==74: assert self.r.index_2_physical[i] == 72
            elif (75<=i) & (i<=99): assert self.r.index_2_physical[i] == 99-i+47
            elif (100<=i) & (i<=139): assert self.r.index_2_physical[i] == i-100
            elif (140<=i) & (i<=145): assert self.r.index_2_physical[i] == i-100+1
            elif i==148: assert self.r.index_2_physical[i] == 149
            elif i==149: assert self.r.index_2_physical[i] == 148
            else: assert self.r.index_2_physical[i] == i
        #-------------End check-------------#
    
    def test_same_hot_data(self):
        
        #------------1 times GC------------#
        for j in range(100):
            self.r.write(d=0, lb=0, lp=j)
        for i in range(73):
            for j in range(100):
                self.r.write(d=0, lb=0, lp=99)
        for i in range(1):
            for j in range(100):
                self.r.write(d=0, lb=0, lp=99)
        #------------Start check------------#
        # parameter
        assert self.r.l_clean_counter == 1
        assert self.r.l_act_block_index_p == 74
        assert self.r.l_act_page_p == 0
        assert self.r.h_clean_counter == 73
        assert self.r.h_act_block_index_p == 76
        assert self.r.h_act_page_p == 0
        # clean
        for i in range(150):
            if i==74: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif i==76: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif (0<=i) & (i<72): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==72: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif i==73: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==74: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif (75<=i) & (i<76): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            else: assert self.r.clean[self.r.index_2_physical[i]] == True
        # erase_count_index
        for i in range(150):
            if i<1: assert self.r.erase_count_index[i] == 149
            else: assert self.r.erase_count_index[i] == 150
        # index_2_physical
        for i in range(150):
            if i==72: assert self.r.index_2_physical[i] == 149
            elif i==149: assert self.r.index_2_physical[i] == 72
            else: assert self.r.index_2_physical[i] == i
        #-------------End check-------------#
        
        #------------2 times GC------------#
        for i in range(1):
            for j in range(100):
                self.r.write(d=0, lb=0, lp=99)
        #------------Start check------------#
        # parameter
        assert self.r.l_clean_counter == 1
        assert self.r.l_act_block_index_p == 72
        assert self.r.l_act_page_p == 0
        assert self.r.h_clean_counter == 73
        assert self.r.h_act_block_index_p == 76
        assert self.r.h_act_page_p == 0
        # clean
        for i in range(150):
            if i==72: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif i==76: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif (0<=i) & (i<72): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==72: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==73: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif i==74: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif (75<=i) & (i<76): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            else: assert self.r.clean[self.r.index_2_physical[i]] == True
        # erase_count_index
        for i in range(150):
            if i<1: assert self.r.erase_count_index[i] == 148
            else: assert self.r.erase_count_index[i] == 150
        # index_2_physical
        for i in range(150):
            if i==72: assert self.r.index_2_physical[i] == 149
            elif i==73: assert self.r.index_2_physical[i] == 148
            elif i==148: assert self.r.index_2_physical[i] == 73
            elif i==149: assert self.r.index_2_physical[i] == 72
            else: assert self.r.index_2_physical[i] == i
        #-------------End check-------------#
        
        #------------3 times GC------------#
        for i in range(1):
            for j in range(100):
                self.r.write(d=0, lb=0, lp=99)
        #------------Start check------------#
        # parameter
        assert self.r.l_clean_counter == 1
        assert self.r.l_act_block_index_p == 73
        assert self.r.l_act_page_p == 0
        assert self.r.h_clean_counter == 73
        assert self.r.h_act_block_index_p == 76
        assert self.r.h_act_page_p == 0
        # clean
        for i in range(150):
            if i==73: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif i==76: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif (0<=i) & (i<72): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif i==72: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==73: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==74: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif (75<=i) & (i<76): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            else: assert self.r.clean[self.r.index_2_physical[i]] == True
        # erase_count_index
        for i in range(150):
            if i<1: assert self.r.erase_count_index[i] == 147
            else: assert self.r.erase_count_index[i] == 150
        # index_2_physical
        for i in range(150):
            if i==72: assert self.r.index_2_physical[i] == 149
            elif i==73: assert self.r.index_2_physical[i] == 148
            elif i==74: assert self.r.index_2_physical[i] == 147
            elif i==147: assert self.r.index_2_physical[i] == 74
            elif i==148: assert self.r.index_2_physical[i] == 73
            elif i==149: assert self.r.index_2_physical[i] == 72
            else: assert self.r.index_2_physical[i] == i
        #-------------End check-------------#
        
        #------------73 times GC------------#
        for i in range(70):
            for j in range(100):
                self.r.write(d=0, lb=0, lp=99)
        #------------Start check------------#
        # parameter
        assert self.r.l_clean_counter == 1
        assert self.r.l_act_block_index_p == 74
        assert self.r.l_act_page_p == 0
        assert self.r.h_clean_counter == 73
        assert self.r.h_act_block_index_p == 76
        assert self.r.h_act_page_p == 0
        # clean
        for i in range(150):
            if i==74: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif i==76: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif (0<=i) & (i<72): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==72: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif i==73: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==74: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif (75<=i) & (i<76): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            else: assert self.r.clean[self.r.index_2_physical[i]] == True
        # erase_count_index
        for i in range(150):
            if i<1: assert self.r.erase_count_index[i] == 77
            else: assert self.r.erase_count_index[i] == 150
        # index_2_physical
        for i in range(150):
            if i==72: assert self.r.index_2_physical[i] == 77
            elif i==73: assert self.r.index_2_physical[i] == 79
            elif i==74: assert self.r.index_2_physical[i] == 78
            elif (77<=i) & (i<=146): assert self.r.index_2_physical[i] == i+3
            elif i==147: assert self.r.index_2_physical[i] == 74
            elif i==148: assert self.r.index_2_physical[i] == 73
            elif i==149: assert self.r.index_2_physical[i] == 72
            else: assert self.r.index_2_physical[i] == i
        #-------------End check-------------#
        
        #------------74 times GC------------#
        for i in range(1):
            for j in range(100):
                self.r.write(d=0, lb=0, lp=99)
        #------------Start check------------#
        # parameter
        assert self.r.l_clean_counter == 0
        assert self.r.l_act_block_index_p == 72
        assert self.r.l_act_page_p == 0
        assert self.r.h_clean_counter == 74
        assert self.r.h_act_block_index_p == 73
        assert self.r.h_act_page_p == 0
        # clean
        for i in range(150):
            if i==72: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif i==73: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif (0<=i) & (i<72): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==72: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==73: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif i==74: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif (75<=i) & (i<76): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            else: assert self.r.clean[self.r.index_2_physical[i]] == True
        # erase_count_index
        for i in range(150):
            if i<1: assert self.r.erase_count_index[i] == 76
            else: assert self.r.erase_count_index[i] == 150
        # index_2_physical
        for i in range(150):
            if i==72: assert self.r.index_2_physical[i] == 77
            elif i==73: assert self.r.index_2_physical[i] == 76
            elif i==74: assert self.r.index_2_physical[i] == 78
            elif (76<=i) & (i<=146): assert self.r.index_2_physical[i] == i+3
            elif i==147: assert self.r.index_2_physical[i] == 74
            elif i==148: assert self.r.index_2_physical[i] == 73
            elif i==149: assert self.r.index_2_physical[i] == 72
            else: assert self.r.index_2_physical[i] == i
        #-------------End check-------------#
        
        #------------75 times GC------------#
        #for i in range(1):
        for j in range(1):
            self.r.write(d=0, lb=0, lp=99)
        #------------Start check------------#
        # parameter
        assert self.r.l_clean_counter == 0
        assert self.r.l_act_block_index_p == 72
        assert self.r.l_act_page_p == 1
        assert self.r.h_clean_counter == 75
        assert self.r.h_act_block_index_p == 73
        assert self.r.h_act_page_p == 0
        # clean
        for i in range(150):
            if i==72: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif i==73: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif (0<=i) & (i<72): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==72: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==73: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif i==74: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif (75<=i) & (i<76): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            else: assert self.r.clean[self.r.index_2_physical[i]] == True
        # erase_count_index
        for i in range(150):
            if i<1: assert self.r.erase_count_index[i] == 75
            else: assert self.r.erase_count_index[i] == 150
        # index_2_physical
        for i in range(150):
            if i==72: assert self.r.index_2_physical[i] == 77
            elif i==73: assert self.r.index_2_physical[i] == 76
            elif i==74: assert self.r.index_2_physical[i] == 75
            elif (75<=i) & (i<=146): assert self.r.index_2_physical[i] == i+3
            elif i==147: assert self.r.index_2_physical[i] == 74
            elif i==148: assert self.r.index_2_physical[i] == 73
            elif i==149: assert self.r.index_2_physical[i] == 72
            else: assert self.r.index_2_physical[i] == i
        #-------------End check-------------#
        
        #------------76 times GC------------#
        #for i in range(1):
        for j in range(1):
            self.r.write(d=0, lb=0, lp=99)
        #------------Start check------------#
        # parameter
        assert self.r.l_clean_counter == 1
        assert self.r.l_act_block_index_p == 72
        assert self.r.l_act_page_p == 2
        assert self.r.h_clean_counter == 75
        assert self.r.h_act_block_index_p == 73
        assert self.r.h_act_page_p == 0
        # clean
        for i in range(150):
            if i==72: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif i==73: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif (0<=i) & (i<72): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==72: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==73: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==74: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif (75<=i) & (i<76): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            else: assert self.r.clean[self.r.index_2_physical[i]] == True
        # erase_count_index
        for i in range(150):
            if i<1: assert self.r.erase_count_index[i] == 74
            else: assert self.r.erase_count_index[i] == 150
        # index_2_physical
        for i in range(150):
            if i==71: assert self.r.index_2_physical[i] == 75
            elif i==72: assert self.r.index_2_physical[i] == 77
            elif i==73: assert self.r.index_2_physical[i] == 76
            elif i==74: assert self.r.index_2_physical[i] == 71
            elif (75<=i) & (i<=146): assert self.r.index_2_physical[i] == i+3
            elif i==147: assert self.r.index_2_physical[i] == 74
            elif i==148: assert self.r.index_2_physical[i] == 73
            elif i==149: assert self.r.index_2_physical[i] == 72
            else: assert self.r.index_2_physical[i] == i
        #-------------End check-------------#
            
        #------------77 times GC------------#
        #for i in range(1):
        for j in range(100):
            self.r.write(d=0, lb=0, lp=99)
        #------------Start check------------#
        # parameter
        assert self.r.l_clean_counter == 1
        assert self.r.l_act_block_index_p == 74
        assert self.r.l_act_page_p == 2
        assert self.r.h_clean_counter == 75
        assert self.r.h_act_block_index_p == 70
        assert self.r.h_act_page_p == 0
        # clean
        for i in range(150):
            if i==74: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif i==70: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif (0<=i) & (i<72): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif i==72: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==73: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==74: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif (75<=i) & (i<76): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            else: assert self.r.clean[self.r.index_2_physical[i]] == True
        # erase_count_index
        for i in range(150):
            if i<1: assert self.r.erase_count_index[i] == 73
            else: assert self.r.erase_count_index[i] == 150
        # index_2_physical
        for i in range(150):
            if i==70: assert self.r.index_2_physical[i] == 76
            elif i==71: assert self.r.index_2_physical[i] == 75
            elif i==72: assert self.r.index_2_physical[i] == 77
            elif i==73: assert self.r.index_2_physical[i] == 70
            elif i==74: assert self.r.index_2_physical[i] == 71
            elif (75<=i) & (i<=146): assert self.r.index_2_physical[i] == i+3
            elif i==147: assert self.r.index_2_physical[i] == 74
            elif i==148: assert self.r.index_2_physical[i] == 73
            elif i==149: assert self.r.index_2_physical[i] == 72
            else: assert self.r.index_2_physical[i] == i
        #-------------End check-------------#
            
        #------------78 times GC------------#
        #for i in range(1):
        for j in range(100):
            self.r.write(d=0, lb=0, lp=99)
        #------------Start check------------#
        # parameter
        assert self.r.l_clean_counter == 1
        assert self.r.l_act_block_index_p == 73
        assert self.r.l_act_page_p == 2
        assert self.r.h_clean_counter == 75
        assert self.r.h_act_block_index_p == 70
        assert self.r.h_act_page_p == 0
        # clean
        for i in range(150):
            if i==73: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif i==70: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif (0<=i) & (i<72): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==72: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==73: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif i==74: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif (75<=i) & (i<76): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            else: assert self.r.clean[self.r.index_2_physical[i]] == True
        # erase_count_index
        for i in range(150):
            if i<1: assert self.r.erase_count_index[i] == 72
            else: assert self.r.erase_count_index[i] == 150
        # index_2_physical
        for i in range(150):
            if i==70: assert self.r.index_2_physical[i] == 76
            elif i==71: assert self.r.index_2_physical[i] == 75
            elif i==72: assert self.r.index_2_physical[i] == 77
            elif i==73: assert self.r.index_2_physical[i] == 70
            elif i==74: assert self.r.index_2_physical[i] == 71
            elif (75<=i) & (i<=146): assert self.r.index_2_physical[i] == i+3
            elif i==147: assert self.r.index_2_physical[i] == 74
            elif i==148: assert self.r.index_2_physical[i] == 73
            elif i==149: assert self.r.index_2_physical[i] == 72
            else: assert self.r.index_2_physical[i] == i
        #-------------End check-------------#
            
        #------------79 times GC------------#
        #for i in range(1):
        for j in range(100):
            self.r.write(d=0, lb=0, lp=99)
        #------------Start check------------#
        # parameter
        assert self.r.l_clean_counter == 1
        assert self.r.l_act_block_index_p == 72
        assert self.r.l_act_page_p == 2
        assert self.r.h_clean_counter == 75
        assert self.r.h_act_block_index_p == 70
        assert self.r.h_act_page_p == 0
        # clean
        for i in range(150):
            if i==72: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif i==70: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif (0<=i) & (i<72): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==72: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif i==73: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==74: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif (75<=i) & (i<76): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            else: assert self.r.clean[self.r.index_2_physical[i]] == True
        # erase_count_index
        for i in range(150):
            if i<1: assert self.r.erase_count_index[i] == 72
            elif i<2: assert self.r.erase_count_index[i] == 149
            else: assert self.r.erase_count_index[i] == 150
        # index_2_physical
        for i in range(150):
            if i==70: assert self.r.index_2_physical[i] == 76
            elif i==71: assert self.r.index_2_physical[i] == 75
            elif i==72: assert self.r.index_2_physical[i] == 77
            elif i==73: assert self.r.index_2_physical[i] == 70
            elif i==74: assert self.r.index_2_physical[i] == 72
            elif (75<=i) & (i<=146): assert self.r.index_2_physical[i] == i+3
            elif i==147: assert self.r.index_2_physical[i] == 74
            elif i==148: assert self.r.index_2_physical[i] == 73
            elif i==149: assert self.r.index_2_physical[i] == 71
            else: assert self.r.index_2_physical[i] == i
        #-------------End check-------------#
            
        #------------80 times GC------------#
        #for i in range(1):
        for j in range(100):
            self.r.write(d=0, lb=0, lp=99)
        #------------Start check------------#
        # parameter
        assert self.r.l_clean_counter == 1
        assert self.r.l_act_block_index_p == 74
        assert self.r.l_act_page_p == 2
        assert self.r.h_clean_counter == 75
        assert self.r.h_act_block_index_p == 70
        assert self.r.h_act_page_p == 0
        # clean
        for i in range(150):
            if i==74: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif i==70: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif (0<=i) & (i<72): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif i==72: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==73: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==74: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif (75<=i) & (i<76): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            else: assert self.r.clean[self.r.index_2_physical[i]] == True
        # erase_count_index
        for i in range(150):
            if i<1: assert self.r.erase_count_index[i] == 72
            elif i<2: assert self.r.erase_count_index[i] == 148
            else: assert self.r.erase_count_index[i] == 150
        # index_2_physical
        for i in range(150):
            if i==70: assert self.r.index_2_physical[i] == 76
            elif i==71: assert self.r.index_2_physical[i] == 75
            elif i==72: assert self.r.index_2_physical[i] == 77
            elif i==73: assert self.r.index_2_physical[i] == 73
            elif i==74: assert self.r.index_2_physical[i] == 72
            elif (75<=i) & (i<=146): assert self.r.index_2_physical[i] == i+3
            elif i==147: assert self.r.index_2_physical[i] == 74
            elif i==148: assert self.r.index_2_physical[i] == 70
            elif i==149: assert self.r.index_2_physical[i] == 71
            else: assert self.r.index_2_physical[i] == i
        #-------------End check-------------#
    
    def _test_all_hot_data(self):
        
        #------------1 times GC------------#
        for i in range(73):
            for j in range(100):
                self.r.write(d=0, lb=i, lp=j)
                self.r.write(d=0, lb=i, lp=j)
        #------------Start check------------#
        # parameter
        assert self.r.l_clean_counter == 1
        assert self.r.l_act_block_index_p == 74
        assert self.r.l_act_page_p == 0
        assert self.r.h_clean_counter == 73
        assert self.r.h_act_block_index_p == 76
        assert self.r.h_act_page_p == 0
        # clean
        for i in range(150):
            if i==74: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif i==76: assert self.r.clean[self.r.index_2_physical[i]] == False # ptr
            elif (0<=i) & (i<72): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==72: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif i==73: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            #elif i==74: assert self.r.clean[self.r.index_2_physical[i]] == False # data
            elif (75<=i) & (i<76): assert self.r.clean[self.r.index_2_physical[i]] == False # data
            else: assert self.r.clean[self.r.index_2_physical[i]] == True
        # erase_count_index
        for i in range(150):
            if i<1: assert self.r.erase_count_index[i] == 149
            else: assert self.r.erase_count_index[i] == 150
        # index_2_physical
        for i in range(150):
            if i==72: assert self.r.index_2_physical[i] == 149
            elif i==149: assert self.r.index_2_physical[i] == 72
            else: assert self.r.index_2_physical[i] == i
        #-------------End check-------------#
    
    
    ##　Bug:  All high # block excepte the high active block are erased min_wear + tau times.
    ##         So we can't find the victim block in high # block list, and error occured
    ##
    ##  Sol: Need data migragtion!
    def _test_write_cold_data_unlimitedly(self):
        
        for i in range(73):
            for j in range(100):
                self.r.write(d=0, lb=i, lp=j)
        for l in range(55):
            for i in range(27):
                for j in range(100):
                    self.r.write(d=0, lb=i, lp=j)
        for i in range(20):
                for j in range(100):
                    self.r.write(d=0, lb=i, lp=j)
        
        ##　will failed at 1673 times gc ##
        #for j in range(100):
        #    self.r.write(d=0, lb=i, lp=j)
    
    ## Bug: Unfind, maybe just like bug in test_write_cold_data_unlimitedly()
    ##
    ## Sol: None
    def _test_write_hot_data_unlimitedly(self): ##　will failed at 5962 times gc ##
        
        for j in range(100):
            self.r.write(d=0, lb=0, lp=j)
        for i in range(6000):
            for j in range(100):
                self.r.write(d=0, lb=0, lp=99)
        
        