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

        self.n_page = n_page  # number of pages in a block
        self.n_log_blocks = n_log_blocks  # number of logical block
        self.n_phy_blocks = n_phy_blocks  # number of physical block
        self.clean = [True] * self.n_phy_blocks  # clean bit for physical block
        """
            Rejuvenator index data structure
            index_2_physical : it is index for each physical block 
            erase_count_index : it is seperator to separate each regions with same erase count
            
            Examples
            index_2_physical: a[1,5,7,3,2]  a[0] means the physical block 1, a[2] means the physical block 7
            erase_count_index: [2,2,1] means a[0:2] have erase count 0
                                             a[2:2+2] have erase count 1
                                             a[4] have erase count 2
                                             
            FYI a[x:y] means a[x],a[x+1]....a[y-1]
        """
        self.index_2_physical = [i for i in range(n_phy_blocks)]  # erase count for physical block [0 ... n_phy_block-1]
        self.erase_count_index = [-1] * self.n_phy_blocks  # erase count separator
        self.erase_count_index[0] = n_phy_blocks

        self.h_act_block_index_p = -1  # high active block pointer based on index_2_physical
        self.h_act_page_p = -1  # high active page pointer for physical page
        self.l_act_block_index_p = 0  # low active block pointer ..
        self.l_act_page_p = 0  # low active page pointer ..

        self.l_to_p = [[-1] * n_page for _ in range(n_log_blocks)]  # logical to physical block mapping
        self.phy_page_info = [['c'] * n_page for _ in range(n_phy_blocks)]  # page information it can be "i":invalid,
        # "c": clean, or int:
        # logical address (lb,lp)
        self.l_clean_counter = self.n_phy_blocks  # number of clean blocks in the lower number list
        self.h_clean_counter = self.n_phy_blocks  # number of clean blocks in the higher number list

        self.LRU = [None] * lru_size  # LRU

        self.tau = tau  # tau value
        self.m = m

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
            if self.h_act_block_index_p != -1:
                pb, pp = self.index_2_physical[self.h_act_block_index_p], self.h_act_page_p
                self._w(d, pb, pp)  # write data
                self._update_lru(lb, lp)

                #  update logical to physical mapping
                if self.l_to_p[lb][lp] != -1:  # clean previous physical address from the same logical address
                    pb, pp = self.l_to_p[lb][lp]
                    self.phy_page_info[pb][pp] = 'i'

                self.l_to_p[lb][lp] = pb, pp

                # update active pointer value
                if self.h_act_page_p + 1 == self.n_page:
                    # page + 1 == block size
                    # move the high pointer to the next clean block
                    # search a clean block from the head of the high number list
                    self.h_act_page_p = 0
                    self.h_act_block_index_p = self._get_head_idx(erase_count=self.min_wear() + self.m)
                    while not self.clean[self.index_2_physical[self.h_act_block_index_p]]:
                        self.h_act_block_index_p += 1

                    self.h_clean_counter -= 1
                    self.clean[self.index_2_physical[self.h_act_block_index_p]] = False

                    if self.h_clean_counter < 1:  # if there is no clean block then GC
                        self.gc()

                else:
                    # page + 1 < block size
                    self.h_act_page_p += 1

            else:
                # no high block e.g. initial states where all blocks whose erase count = 0
                # similarly write it the lower number list
                pass
        else:
            # similarly write it the lower number list

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
        v_idx, v_pb = self._find_vb(erase_count_start=0, erase_count_end=self.n_phy_blocks - 1)
        self._erase_block_data(pb=v_pb)

        # check lower number list
        if self.l_clean_counter < 1:
            l_vic_idx, l_vic_pb = self._find_vb(erase_count_start=self.min_wear(),
                                                erase_count_end=self.min_wear() + self.m
                                                )
            self._erase_block_data(pb=l_vic_pb)

        elif self.h_clean_counter < 1:
            # check higher number list
            h_vic_idx, h_vic_pb = self._find_vb(erase_count_start=self.min_wear() + self.m,
                                                erase_count_end=self.max_wear() + 1
                                                )
            self._erase_block_data(pb=h_vic_pb)

    def data_migration(self):
        idx = self._get_most_clean_efficient_block_idx()
        if self.min_wear() <= self._get_erase_count_by_idx(idx) < self.min_wear() + self.tau:
            idx = self._get_head_idx(erase_count=self.min_wear())
            end_idx = self._get_head_idx(erase_count=self.min_wear() + 1)

            while idx < end_idx:
                pb = self.index_2_physical[idx]
                self._erase_block_data(pb=pb)
                idx += 1

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

    def min_wear(self):
        return 0

    def max_wear(self):
        return 10000

    def _find_vb(self, erase_count_start, erase_count_end):
        """
        find a victim block from [erase_count_start, erase_count_end)
        :return idx,B
        """
        idx = self._get_head_idx(erase_count=erase_count_start)
        end_idx = self._get_head_idx(erase_count=erase_count_end)
        most_clean_idx, n_of_max_invalid_page = idx, 0

        while idx != end_idx:
            pd = self.index_2_physical[idx]
            n_of_invalid_page = sum([1 if page == "i" else 0
                                     for page in self.phy_page_info[pd]]
                                    )
            if n_of_invalid_page >= n_of_max_invalid_page:
                most_clean_idx = idx
                n_of_max_invalid_page = n_of_invalid_page
            idx += 1

        return most_clean_idx, self.index_2_physical[most_clean_idx]

    def _update_lru(self, lb, lp):
        pass

    def _get_head_idx(self, erase_count=0):
        return sum(self.erase_count_index[:erase_count])

    def _erase_block_data(self, pb):

        pp = 0
        """         
            loop invariant 0 <= page <= self.n_page
            loop invariant \forall int j; 0 <= j < i ==> self.page_info[b][page] == 'c' || self.page_info[b][page] == 'i'
            loop assigns page, self.page_info[b][0 .. self.n_page -1]
            loop variant self.n_page - page  
            
            
            loop assigns self.h_act_block_p, self.h_act_page_p
            loop assigns self.l_act_block_p, self.l_act_page_p
        """
        # move all pages in the block
        while pp != self.n_page:
            if not self.phy_page_info[pb][pp] in ['c', 'i']:  # move valid page
                lb, lp = self.phy_page_info[pb][pp]
                self._write_without_gc(self._r(pb, pp), lb, lp)

            self.phy_page_info[pb][pp] = 'c'  # set to a clean page
            pp += 1

        # erase the block
        self._erase_block(pb=pb)

        # special case for high number block index
        if self.h_act_block_index_p == -1:  # initially it is -1 but some block whose erase count will be over
            # min_wear+m
            idx = self.index_2_physical.index(pb)
            if self._get_erase_count_by_idx(idx) >= self.min_wear() + self.m:
                self.h_act_block_index_p = idx
                self.h_clean_counter = 1

    def _erase_block(self, pb):
        """
            erase block and update index_2_physical & erase_count_index
        :param pb:
        :return:
        """
        pass

    def _get_most_clean_efficient_block_idx(self):
        most_clean_idx, n_of_max_invalid_page = 0, 0

        for idx in range(len(self.index_2_physical)):
            pd = self.index_2_physical[idx]
            n_of_invalid_page = 0

            for page in self.phy_page_info[pd]:
                if page == "i":
                    n_of_invalid_page += 1

            if n_of_invalid_page >= n_of_max_invalid_page:
                n_of_max_invalid_page = n_of_invalid_page
                most_clean_idx = idx

        return most_clean_idx

    def _get_erase_count_by_idx(self, idx):
        cur = 0
        for erase_count in range(len(self.erase_count_index)):
            if cur + self.erase_count_index[erase_count] > idx:
                return erase_count
            else:
                cur = cur + self.erase_count_index[erase_count]

        return len(self.erase_count_index)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    r = Rejuvenator()
