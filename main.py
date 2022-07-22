class Rejuvenator:
    """
    Rejuvenator prototype
    """

    def __init__(self, n_phy_blocks=150, n_log_blocks=100, m=10, n_page=100, lru_size=100, tau=20):
        """
        Initialize the Rejuvenator

        :param n_phy_blocks: number of physical blocks
        :param n_log_blocks: number of logical blocks
        :param m: parameter for m value
        :param n_page: number of pages per block
        :param lru_size: lru size by page
        """
        self.m = m
        self.n_page = n_page  # number of pages in a block
        self.n_log_blocks = n_log_blocks  # number of logical block
        self.n_phy_blocks = n_phy_blocks  # number of physical block
        self.clean = [True] * self.n_phy_blocks  # clean bit for physical block
        # TODO more examples
        self.index_2_physical = [i for i in range(n_phy_blocks)]  # erase count for physical block [0 ... n_phy_block-1]
        self.erase_count_index = [-1] * self.n_phy_blocks  # erase count separator
        self.erase_count_index[0] = n_phy_blocks - 1

        self.h_act_block_p = 0  # high active block pointer based on index_2_physical
        self.h_act_page_p = 0  # high active page pointer ..
        self.l_act_block_p = 0  # low active block pointer ..
        self.l_act_page_p = 0  # low active page pointer ..

        self.l_to_p = [[-1] * n_page for _ in range(n_log_blocks)]  # logical to physical block mapping
        self.phy_page_info = [['c'] * n_page for _ in range(n_phy_blocks)]  # page information it can be "i":invalid,
        # "c": clean, or int:
        # logical address (lb,lp)
        self.l_clean_counter = self.n_phy_blocks  # number of clean blocks in the lower number list
        self.h_clean_counter = self.n_phy_blocks  # number of clean blocks in the higher number list

        self.LRU = [None] * lru_size  # LRU

        self.tau = tau  # delta value

        self.min_wear = 0
        self.max_wear = 200

    def write(self, d, lb, lp):
        """
        write the data d based on the logical address (lb,lp)
        :param d: data
        :param lb: logical block
        :param lp: logical page
        :return:

        precondition
            requires l_clean_counter > 0 && h_clean_counter > 0
        post-condition
        """
        # check the logical address is hot or cold
        if (lb, lp) not in self.LRU:
            # cold data
            # see if the block is in the high number list or lower number list
            # if self._is_high_n_list(self.l_to_p[lb]):
            self._w(d, self.h_act_block_p, self.h_act_page_p)  # write data
            self._update_lru(lb, lp)

            if self.l_to_p[lb][lp] != -1:  # clean previous physical address from the same logical address
                pb, pp = self.l_to_p[lb][lp]
                self.phy_page_info[pb][pp] = 'i'

            self.phy_page_info[self.h_act_block_p][self.h_act_page_p] = (lb, lp)
            self.l_to_p[lb][lp] = (self.h_act_page_p,self.h_act_page_p)
            
            # update active high page pointer
            if self.h_act_page_p + 1 == self.n_page:
                # page + 1 == block size
                # move the high pointer to the next clean block
                self.h_act_page_p = 0

                # search a clean block from the head of the high number list

                self.h_act_block_p = self._get_head(erase_count=self.min_wear+self.m)

                while self.h_act_block_p != len(self.index_2_physical) and self.clean[self._index_2_physical(self.h_act_block_p)]:
                    self.h_act_block_p += 1

                self.h_clean_counter -= 1
                self.clean[self.h_act_block_p] = False

                if self.h_clean_counter < 1:  # if there is no clean block then GC
                    self.gc()

            else:
                # page + 1 < block size
                self.h_act_page_p += 1

            # else:
            #     # similarly
            #     pass
        else:
            # similarly
            # hot data

            pass

    def _write_without_gc(self, d, lb, lp):
        """
        same as write but without gc

        :param d: data
        :param lb: logical block address
        :param lp: logical page number
        :return:
        """
        pass

    def gc(self):
        """
        perform garbage collection to ensure there is at least one clean block
        :return:
        """
        idx, b = self._find_vb()
        page = 0

        """         
         loop invariant 0 <= page <= self.n_page
         loop invariant \forall int j; 0 <= j < i ==> self.page_info[b][page] == 'c' || self.page_info[b][page] == 'i'
         loop assigns page, self.page_info[b][0 .. self.n_page -1]
         loop variant self.n_page - page  
         
          
         loop assigns self.h_act_block_p, self.h_act_page_p
         loop assigns self.l_act_block_p, self.l_act_page_p
        """
        while page != self.n_page:
            if not self.phy_page_info[b][page] in ['c', 'i']:  # move valid page
                lb, lp = self.phy_page_info[b][page]
                self._write_without_gc(self._r(b, page), lb, lp)

            self.phy_page_info[b][page] = 'c'  # set to a clean page
            page += 1

        # check lower number list

        # check higher number list


    def data_migration(self):
        pass

    def _w(self, d, pb, pg):
        """
        write data to physical address
        :param d: data
        :param pb: physical block
        :param pg: physical page
        :return:
        """

        pass

    def _r(self, pb, pg):
        """
        read from physical block address and page number
        :param pb: physical block address
        :param pg: physical page number
        :return:
        """
        pass

    def _find_vb(self):
        """
        find a victim block
        :return idx,B
        """
        return 1, 1

    def _update_lru(self, lb, lp):
        pass

    def _get_head(self,erase_count=0):
        return 0

    def _index_2_physical(self,idx=0):
        return self.index_2_physical[idx]

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    r = Rejuvenator()
    r.write(d="a",lb=0,lp=1)
    r.gc()
