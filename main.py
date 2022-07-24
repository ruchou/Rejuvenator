class Rejuvenator:
    """
    Rejuvenator prototype
    """

    def __init__(self, n_phy_blocks=150, n_log_blocks=100, n_page=100, lru_size=100, tau=20):
        """
        Initialize the Rejuvenator

        :param n_phy_blocks: number of physical blocks
        :param n_log_blocks: number of logical blocks
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
            

            index_2_physical: a[1,5,7,3,2]  a[0] means the physical block 1, a[2] means the physical block 7
            erase_count_index: [2,4,5] means a[0:2] have erase count 0
                                             a[2:4] have erase count 1
                                             a[4:5] have erase count 2
            erase count 0: index_2_physical[0,erase_count_index[0])
                        1: index_2_physical[erase_count_index[0],erase_count_index[1])
                        2: index_2_physical[erase_count_index[1],erase_count_index[2])
                        i: index_2_physical[erase_count_index[i-1],erase_count_index[i])
                                            
            erase_count_index: [0,0,0,3,3,5] means a[0:3] have erase count 3
                                                   a[3:5] have erase count 5
                                                           
            FYI a[x:y] means a[x],a[x+1]....a[y-1]
        """
        self.index_2_physical = [i for i in range(n_phy_blocks)]  # erase count for physical block [0 ... n_phy_block-1]
        self.erase_count_index = [0] * self.n_phy_blocks  # erase count separator
        self.erase_count_index[0] = n_phy_blocks

        self.h_act_block_index_p = n_phy_blocks // 2  # high active block pointer based on index_2_physical
        self.h_act_page_p = 0  # high active page pointer for physical page
        self.l_act_block_index_p = 0  # low active block pointer ..
        self.l_act_page_p = 0  # low active page pointer ..

        self.l_to_p = [[-1] * n_page for _ in range(n_log_blocks)]  # logical to physical block mapping
        self.phy_page_info = [['c'] * n_page for _ in range(n_phy_blocks)]  # page information it can be "i":invalid,
        # "c": clean, or int:
        # logical address (lb,lp)
        self.l_clean_counter = self.n_phy_blocks // 2  # number of clean blocks in the lower number list
        self.h_clean_counter = self.n_phy_blocks - self.l_clean_counter  # number of clean blocks in the higher
        # number list

        self.LRU = [None] * lru_size  # LRU

        self.tau = tau  # tau value

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
        self._write_helper(d=d, lb=lb, lp=lp)
        if self.h_clean_counter < 1:  # if there is no clean block then GC
            self.gc()

    def _write_helper(self, d, lb, lp):
        """
        same as write but without gc

        :param d: data
        :param lb: logical block address
        :param lp: logical page number
        :return:
        """
        # check the logical address is hot or cold
        if (lb, lp) not in self.LRU:
            # cold data
            self._write_2_higher_number_list(d, lb, lp)
        else:
            # hot data
            if self.l_act_block_index_p == -1:
                # if there is no clean block in the lower number list, write to the higher number list
                self._write_2_higher_number_list(d, lb, lp)
            else:  # write to the lower number list
                self._write_2_lower_number_list(d, lb, lp)

    def _write_2_higher_number_list(self, d, lb, lp):
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
            self.h_act_block_index_p = self.n_phy_blocks // 2

            while not self.clean[self.index_2_physical[self.h_act_block_index_p]]:
                self.h_act_block_index_p += 1

            self.h_clean_counter -= 1
            self.clean[self.index_2_physical[self.h_act_block_index_p]] = False
        else:
            # page + 1 < block size
            self.h_act_page_p += 1

    def _write_2_lower_number_list(self, d, lb, lp):
        pb, pp = self.index_2_physical[self.l_act_block_index_p], self.l_act_page_p
        self._w(d, pb, pp)  # write data
        self._update_lru(lb, lp)

        #  update logical to physical mapping
        if self.l_to_p[lb][lp] != -1:  # clean previous physical address from the same logical address
            pb, pp = self.l_to_p[lb][lp]
            self.phy_page_info[pb][pp] = 'i'
        self.l_to_p[lb][lp] = pb, pp

        # update active pointer value
        if self.l_act_page_p + 1 == self.n_page:
            # page + 1 == block size
            # move the high pointer to the next clean block
            # search a clean block from the head of the high number list
            self.l_act_block_index_p = 0

            while not self.clean[self.index_2_physical[self.l_act_block_index_p]]:
                self.l_act_block_index_p += 1

            self.l_clean_counter -= 1
            self.clean[self.index_2_physical[self.l_act_block_index_p]] = False
        else:
            # page + 1 < block size
            self.l_act_page_p += 1

    def gc(self):
        """
        perform garbage collection to ensure there is at least one clean block
        :return:
        """

        # check lower number list
        if self.l_clean_counter < 1:  # [start,end)
            l_vic_idx, l_vic_pb = self._find_vb(start_idx=0,
                                                end_idx=self.n_phy_blocks // 2
                                                )
            self._erase_block_data(idx=l_vic_idx)

        elif self.h_clean_counter < 1:
            # check higher number list
            h_vic_idx, h_vic_pb = self._find_vb(start_idx=self.n_phy_blocks // 2,
                                                end_idx=self.n_phy_blocks
                                                )
            self._erase_block_data(idx=h_vic_idx)
        else:
            v_idx, v_pb = self._find_vb(start_idx=0,
                                        end_idx=self.n_phy_blocks
                                        )
            self._erase_block_data(idx=v_idx)

    def data_migration(self):
        """
        Data Migration
        :return:
        """
        idx = self._get_most_clean_efficient_block_idx()
        if self.min_wear() + self.tau <= self._get_erase_count_by_idx(idx):
            idx = self.erase_count_index[self.min_wear() - 1]
            end_idx = self.erase_count_index[self.min_wear()]

            while idx < end_idx:
                self._erase_block_data(idx=idx)
                idx += 1

    def _w(self, d, pb, pg):
        """
        API
        write data to physical address
        :param d: data
        :param pb: physical block
        :param pg: physical page
        :return:
        """

        pass

    def _r(self, pb, pg):
        """
        API
        read from physical block address and page number
        :param pb: physical block address
        :param pg: physical page number
        :return:
        """
        pass

    def min_wear(self):
        """
        Get the min_wear value
        :return: min_wear value
        """
        for i in range(len(self.erase_count_index)):
            if self.erase_count_index[i] != 0:
                return i

        return self.n_phy_blocks

    def max_wear(self):
        """
        Get the max_wear value
        :return: max_wear value
        """

        for i in range(len(self.erase_count_index)):
            if self.erase_count_index[i] == self.n_phy_blocks:
                return i

    def _find_vb(self, start_idx, end_idx):
        # TODO not  < min_wear + tau break
        # not any active pointer
        """
        find a victim block from [erase_count_start, erase_count_end)
        :return idx,B
        """
        idx = start_idx
        vic_idx, n_of_max_invalid_or_clean_page = idx, 0

        while idx != end_idx:
            pd = self.index_2_physical[idx]

            # ignore the block within the min_wear + tau
            if self._get_erase_count_by_idx(idx) >= self.min_wear() + self.tau:
                continue

            # ignore the block indexed by either active pointer
            if idx == self.h_act_block_index_p or idx == self.l_act_block_index_p:
                continue

            # ignore the block with all clean pages
            if all([True if page == "c" else False for page in self.phy_page_info[pd]]
                   ):
                continue

            n_of_invalid_or_clean_page = sum([1 if page == "i" or page == "c" else 0
                                              for page in self.phy_page_info[pd]]
                                             )

            if n_of_invalid_or_clean_page >= n_of_max_invalid_or_clean_page:
                vic_idx = idx
                n_of_max_invalid_or_clean_page = n_of_invalid_or_clean_page
            idx += 1

        return vic_idx, self.index_2_physical[vic_idx]

    def _update_lru(self, lb, lp):
        """
        Update LRU table
        :param lb: logical block address
        :param lp: logical page address
        :return:
        """
        pass

    def _get_head_idx(self, erase_count=0):
        """
        Get the head index of the erase-count in the index_2_physical
        :param erase_count: erase count
        :return: the head index in the index_2_physical
        """
        if erase_count != 0:
            return 0
        else:
            return self.erase_count_index[erase_count - 1]

    def _erase_block_data(self, idx):
        pb = self.index_2_physical[idx]
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
                self._write_helper(self._r(pb, pp), lb, lp)

            self.phy_page_info[pb][pp] = 'c'  # set to a clean page
            pp += 1

        # erase the block
        self._erase_block(pb=pb)
        # update erase count for pb
        self._increase_erase_count(idx)

    def _increase_erase_count(self, idx):
        # swap the index_2_physical[idx] with the element which has teh same erase count
        erase_count = self._get_erase_count_by_idx(idx=idx)
        last_block_idx = self._get_head_idx(erase_count=erase_count + 1)
        self.index_2_physical[idx], self.index_2_physical[last_block_idx] = self.index_2_physical[last_block_idx], \
                                                                            self.index_2_physical[idx]

        # update the erase_count index
        self.erase_count_index[erase_count] -= 1
        self.erase_count_index[erase_count + 1] += 1

    def _erase_block(self, pb):
        """
        API erase block
        :param pb:
        :return:
        """
        pass

    def _get_most_clean_efficient_block_idx(self):
        """
        Get the most clean efficient block idx
        :return: index of the physical block
        """
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
        """
        Get the erase-count of the physical block indexed by idx in the index_2_physical
        :param idx: index in the index_2_physical
        :return: erase count
        """

        for cur in range(self.n_phy_blocks):
            if self.erase_count_index[cur] > idx:
                return cur
        return self.n_phy_blocks


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    r = Rejuvenator()
