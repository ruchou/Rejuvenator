from main import Rejuvenator

if __name__ == '__main__':
    r = Rejuvenator()
    r.n_phy_blocks = 5
    r.index_2_physical = [1, 5, 7, 3, 2]
    r.erase_count_index = [2, 4, 5]

    for i in range(len(r.index_2_physical)):
        print(r._get_erase_count_by_idx(i))

    print(f"min wear is {r.min_wear()}")
    print(f"max wear is {r.max_wear()}")

    print("")
    r.n_phy_blocks = 5
    r.index_2_physical = [1, 5, 7, 3, 2]
    r.erase_count_index = [0, 0, 0, 3, 3, 5]

    for i in range(len(r.index_2_physical)):
        print(r._get_erase_count_by_idx(i))

    print(f"min wear is {r.min_wear()}")
    print(f"max wear is {r.max_wear()}")
