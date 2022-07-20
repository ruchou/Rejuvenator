class Rejuvenator:
    """
    Rejuvenator prototype
    """

    def __init__(self, n_phy_blocks=150, n_log_blocks=100, m=10, n_page=100, lru_size=100):
        """
        Initialize the Rejuvenator

        :param n_phy_blocks: number of physical blocks
        :param n_log_blocks: number of logical blocks
        :param m: parameter for m value
        """
        self.m = m
        self.n_page = n_page  # number of pages in a block
        self.n_log_blocks = n_log_blocks  # number of logical block
        self.n_phy_blocks = n_phy_blocks  # number of physical block
        self.clean = [True] * self.n_phy_blocks  # clean bit for physical block
        self.index = [-1] * self.n_phy_blocks  # write count index for each physical block
        self.write_count_index = [0] * self.n_phy_blocks  # write count

        self.h_act_block_p = 0  # high active block pointer
        self.h_act_page_p = 0  # high active page pointer
        self.l_act_block_p = -1  # low active block pointer
        self.l_act_page_p = -1  # lowe active page pointer

        self.l_to_p = [-1] * self.n_log_blocks  # logical to physical block mapping
        self.page_info = [['c'] * n_page for _ in
                          range(n_phy_blocks)]  # page information it can be "i":invalid, "c": clean, or int:
        # logical address
        self.l_clean_counter = m - self.l_act_block_p  # number of clean blocks in the lower number list
        self.h_clean_count = self.h_act_page_p - m  # number of clean blocks in the higher number list

        self.LRU = [None] * lru_size  # LRU

    def write(self, d, lb, lp):
        """
        write the data d based on the logical address (lb,lp)
        :param d: data
        :param lb: logical block
        :param lp: logical page
        :return:
        """
        # check the logical data is hot or cold
        if (lb, lp) in self.LRU:
            # cold data
            # see if the block is in the high number list or lower number list
            if self._is_high_n_list_l(lb):
                self._w(d, self.h_act_block_p, self.h_act_page_p)  # write data
                self.page_info[self.h_act_block_p][self.h_act_page_p] = (lb, lp)

                # update high number page pointer
                if self.h_act_page_p + 1 == self.n_page:
                    # page + 1 == block size
                    # move the high pointer to the next clean block
                    self.h_act_page_p = 0
                    self.h_act_block_p += 1

                    while not self.clean[self.h_act_block_p] or not self._is_high_n_list_p(self.h_act_block_p):
                        self.h_act_block_p += 1

                    # TODO clean count checking
                    if self.h_clean_count < 1:  # if there is no clean block then GC
                        self.gc()
                    else:
                        return

                else:
                    # page + 1 < block size
                    self.h_act_page_p += 1

            else:
                pass
        else:
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
            if not self.page_info[b][page] in ['c', 'i']:  # move valid page
                lb, lp = self.page_info[b][page]
                self._write_without_gc(self._r(b, page), lb, lp)

            self.page_info[b][page] = 'c'  # set to a clean page
            page += 1

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

    def _is_high_n_list_p(self, pb):
        pass

    def _is_high_n_list_l(self, lb):
        pass


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    r = Rejuvenator()
    r.gc()
