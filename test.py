from main import Rejuvenator

if __name__ == '__main__':
    r = Rejuvenator()
    r.index_2_physical = [1, 5, 7, 3, 2, 6]
    r.erase_count_index = [2, 0, 4]

    for i in range(len(r.index_2_physical)):
        print(r._get_erase_count_by_idx(i))

    head_idx = r._get_head_idx(2)
    print(f"erase_count=2 head is idx:{head_idx} and element {r.index_2_physical[head_idx]}")
