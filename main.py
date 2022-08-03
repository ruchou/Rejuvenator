class Rejuvenator:
    """
    Rejuvenator prototype
    """

    def __init__(self,
                 n_phy_blocks=150,
                 n_log_blocks=100,
                 n_page=100,
                 lru_size=100,
                 tau=20,
                 max_wear_count=10_000_000
                 ):
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
                        1: index_2_physical[erase_count_index[0]:erase_count_index[1])
                        2: index_2_physical[erase_count_index[1]:erase_count_index[2])
                        i: index_2_physical[erase_count_index[i-1]:erase_count_index[i])
                                            
            erase_count_index: [0,0,0,3,3,5] means a[0:3] have erase count 3
                                                   a[3:5] have erase count 5
            FYI a[x:y] means a[x],a[x+1]....a[y-1]
        """
        self.index_2_physical = [i for i in range(n_phy_blocks)]  # erase count for physical block [0 ... n_phy_block-1]
        self.erase_count_index = [n_phy_blocks] * max_wear_count  # erase count separator

        self.h_act_block_index_p = n_phy_blocks // 2  # high active block pointer based on index_2_physical
        self.h_act_page_p = 0  # high active page pointer for physical page
        self.l_act_block_index_p = 0  # low active block pointer ..
        self.l_act_page_p = 0  # low active page pointer ..

        self.l_to_p = [[-1] * n_page for _ in range(n_log_blocks)]  # logical to physical block mapping
        # [lb][lp] -> [pb][pp]
        self.phy_page_info = [[True] * n_page for _ in
                              range(n_phy_blocks)]  # physical page info True: valid,False invalid

        self.l_clean_counter = self.n_phy_blocks // 2  # number of clean blocks in the lower number list
        self.h_clean_counter = self.n_phy_blocks - self.l_clean_counter  # number of clean blocks in the higher
        # number list
        self.LRU = [(None, None)] * lru_size  # LRU
        self.tau = tau  # tau value

        self.max_wear_count = max_wear_count

    def write(self, d, lb, lp):
        """
        write the data d based on the logical address (lb,lp)
        :param d: data
        :param lb: logical block
        :param lp: logical page
        :return:

        invariant: h_clean_counter >= 1
        """
        self._write_helper(d=d, lb=lb, lp=lp)
        self._update_lru(lb, lp)
        if self.h_clean_counter < 1:  # if there is no clean block then GC
            self.gc()

    def _write_helper(self, d, lb, lp):
        """
        write helper

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
            if self.l_clean_counter < 1:
                # if there is no clean block in the lower number list, write to the higher number list
                self._write_2_higher_number_list(d, lb, lp)
            else:  # write to the lower number list
                self._write_2_lower_number_list(d, lb, lp)

    def _write_2_higher_number_list(self, d, lb, lp):
        pb, pp = self.index_2_physical[self.h_act_block_index_p], self.h_act_page_p
        self._w(d, pb, pp)  # write data
        # self._update_lru(lb, lp)

        #  update logical to physical mapping
        if self.l_to_p[lb][lp] != -1:  # clean previous physical address from the same logical address
            pb, pp = self.l_to_p[lb][lp]
            self.phy_page_info[pb][pp] = False
        self.l_to_p[lb][lp] = pb, pp

        # update active pointer value
        if self.h_act_page_p + 1 == self.n_page:
            # page + 1 == block size
            # move the high pointer to the next clean block
            # search a clean block from the head of the high number list
            self.h_clean_counter -= 1
            self.clean[self.index_2_physical[self.h_act_block_index_p]] = False
            self.h_act_page_p = 0

            self.h_act_block_index_p = self.n_phy_blocks // 2
            while not self.clean[
                self.index_2_physical[self.h_act_block_index_p]] and self.h_act_block_index_p < self.n_phy_blocks:
                self.h_act_block_index_p += 1

        else:
            # page + 1 < block size
            self.h_act_page_p += 1

    def _write_2_lower_number_list(self, d, lb, lp):
        pb, pp = self.index_2_physical[self.l_act_block_index_p], self.l_act_page_p
        self._w(d, pb, pp)  # write data
        # self._update_lru(lb, lp)

        #  update logical to physical mapping
        if self.l_to_p[lb][lp] != -1:  # clean previous physical address from the same logical address
            pb, pp = self.l_to_p[lb][lp]
            self.phy_page_info[pb][pp] = False
        self.l_to_p[lb][lp] = pb, pp

        # update active pointer value
        if self.l_act_page_p + 1 == self.n_page:
            # page + 1 == block size
            # move the high pointer to the next clean block
            # search a clean block from the head of the high number list
            self.l_clean_counter -= 1
            self.clean[self.index_2_physical[self.l_act_block_index_p]] = False
            self.l_act_page_p = 0

            self.l_act_block_index_p = 0
            while not self.clean[
                self.index_2_physical[self.l_act_block_index_p]] and self.l_act_block_index_p < self.n_phy_blocks // 2:
                self.l_act_block_index_p += 1

        else:
            # page + 1 < block size
            self.l_act_page_p += 1

    def gc(self):
        """
        perform garbage collection to ensure there is at least one clean block
        :return:
        """

        # check lower number list
        if self.h_clean_counter < 1:
            # check higher number list
            h_vic_idx, h_vic_pb = self._find_vb(start_idx=self.n_phy_blocks // 2,
                                                end_idx=self.n_phy_blocks
                                                )
            self._erase_block_data(idx=h_vic_idx)
        elif self.l_clean_counter < 1:
            l_vic_idx, l_vic_pb = self._find_vb(start_idx=0,
                                                end_idx=self.n_phy_blocks // 2
                                                )
            self._erase_block_data(idx=l_vic_idx)
        else:
            v_idx, v_pb = self._find_vb(start_idx=0,
                                        end_idx=self.n_phy_blocks
                                        )
            self._erase_block_data(idx=v_idx)

    def data_migration(self):
        """
        Data Migration
        """
        idx = self._get_most_clean_efficient_block_idx()
        if self.min_wear() + self.tau <= self._get_erase_count_by_idx(idx):
            if self.min_wear() == 0:
                idx = self.erase_count_index[0]
            else:
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
        for i in range(self.max_wear_count):
            if self.erase_count_index[i] != 0:
                return i

        return self.max_wear_count

    def max_wear(self):
        """
        Get the max_wear value
        :return: max_wear value
        """

        for i in range(self.max_wear_count):
            if self.erase_count_index[i] == self.n_phy_blocks:
                return i

    def _update_lru(self, lb, lp):
        """
        Update LRU table
        :param lb: logical block address
        :param lp: logical page address
        :return:
        """
        if (lb, lp) not in self.LRU:
            # cache does not exist
            # check size
            cur = 0
            while cur < len(self.LRU):
                if self.LRU[cur] == (None, None):
                    break
                cur += 1

            if cur == len(self.LRU):
                # remove first element
                self.LRU = self.LRU[1:] + [(lb, lp)]
            else:
                self.LRU[cur] = (lb, lp)

            # not enough
            pass
        else:
            # (lb,lp) exists
            # remove (lb,lp)
            cur = 0
            while cur < len(self.LRU):
                if self.LRU[cur] == (lb, lp):
                    tmp = cur + 1
                    while tmp < len(self.LRU):
                        self.LRU[cur] = self.LRU[tmp]
                        cur += 1
                        tmp += 1
                    self.LRU[tmp] = (None, None)
                else:
                    cur += 1
            # insert (lb,lp)
            cur = 0
            while cur < len(self.LRU):
                if not self.LRU[cur]:
                    self.LRU[cur] = (lb, lp)
                cur += 1

    def _get_head_idx(self, erase_count=0):
        """
        Get the head index of the erase-count in the index_2_physical
        :param erase_count: erase count
        :return: the head index in the index_2_physical
        """
        if erase_count == 0:
            return 0
        else:
            if self.erase_count_index[erase_count - 1] >= self.erase_count_index[erase_count]:
                # no such head
                return -1
            else:
                return self.erase_count_index[erase_count - 1]

    def _erase_block_data(self, idx):
        pb = self.index_2_physical[idx]
        pp = 0
        # move all pages in the block
        while pp != self.n_page:

            if self.phy_page_info[pb][pp]:
                lb, lp = self.read_spare_area(pb=pb, pp=pp)
                self._write_helper(self._r(pb, pp), lb, lp)

            self.phy_page_info[pb][pp] = False  # invalidate the page

            pp += 1

        # erase the block by disk erase API
        self._erase_block(pb=pb)
        # update clean block
        self.clean[pb] = True
        # update erase count for pb
        self._increase_erase_count(idx)

    def _increase_erase_count(self, idx):
        # swap the index_2_physical[idx] with the element which has teh same erase count
        erase_count = self._get_erase_count_by_idx(idx=idx)
        last_block_idx = self.erase_count_index[erase_count] - 1
        self.index_2_physical[idx], self.index_2_physical[last_block_idx] = self.index_2_physical[last_block_idx], \
                                                                            self.index_2_physical[idx]

        # update the erase_count index
        self.erase_count_index[erase_count] -= 1

        idx = last_block_idx
        # update clean counter
        if idx < self.n_phy_blocks // 2:
            self.l_clean_counter += 1
        else:
            self.h_clean_counter += 1

    def _erase_block(self, pb):
        """
        API erase block
        :param pb:
        :return:
        """
        pass

    def _find_vb(self, start_idx, end_idx):
        """
        find a victim block from [erase_count_start, erase_count_end)
        :return idx,B
        """
        idx = start_idx
        vic_idx, n_of_max_invalid_or_clean_page = idx, 0

        while idx != end_idx:
            pb = self.index_2_physical[idx]

            # ignore the block within the min_wear + tau
            if self._get_erase_count_by_idx(idx) >= self.min_wear() + self.tau:
                idx += 1
                continue

            # ignore the block indexed by either active pointer
            if idx == self.h_act_block_index_p or idx == self.l_act_block_index_p:
                idx += 1
                continue

            # ignore the block with all clean pages
            if self.phy_page_info[pb].count(False) == self.n_page and \
                    all(self.read_spare_area(pb=pb, pp=page) is None for page in range(self.n_page)):
                idx += 1
                continue

            n_of_invalid_or_clean_page = self.phy_page_info[pb].count(False)

            if n_of_invalid_or_clean_page >= n_of_max_invalid_or_clean_page:
                vic_idx = idx
                n_of_max_invalid_or_clean_page = n_of_invalid_or_clean_page
            idx += 1

        return vic_idx, self.index_2_physical[vic_idx]

    def _get_most_clean_efficient_block_idx(self):
        """
        Get the most clean efficient block idx
        :return: index of the physical block
        """
        most_clean_idx, n_of_max_invalid_or_clean_page = 0, 0

        for idx in range(len(self.index_2_physical)):
            pb = self.index_2_physical[idx]
            n_of_invalid_or_clean_page = 0

            # ignore the block indexed by either active pointer
            if idx == self.h_act_block_index_p or idx == self.l_act_block_index_p:
                continue

            # ignore the block with all clean pages
            if self.phy_page_info[pb].count(False) == self.n_page and \
                    all(self.read_spare_area(pb=pb, pp=page) is None for page in range(self.n_page)):
                continue

            n_of_invalid_or_clean_page = self.phy_page_info[pb].count(False)

            if n_of_invalid_or_clean_page >= n_of_max_invalid_or_clean_page:
                n_of_max_invalid_or_clean_page = n_of_invalid_or_clean_page
                most_clean_idx = idx

        return most_clean_idx

    def _get_erase_count_by_idx(self, idx):
        """
        Get the erase-count of the physical block indexed by idx in the index_2_physical
        :param idx: index in the index_2_physical
        :return: erase count
        """

        for cur in range(self.max_wear_count):
            if self.erase_count_index[cur] > idx:
                return cur
        return self.n_phy_blocks

    def read_spare_area(self, pb, pp):
        """
        DISK API
        read physical page info from the space area
        :param pb: physical block address
        :param pp: physical page address
        :return logical address: (int,int) or None
        """
        #  it should be a number
        #  has to translated back to the logical address
        return (10, 10)

    def write_spare_area(self, pb, pp, log_addr):
        """
            DISK API
            write physical page info from the space area
            :param log_addr: logical address (lb,lp)
            :param pb: physical block address
            :param pp: physical page address
        """


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    r = Rejuvenator()
