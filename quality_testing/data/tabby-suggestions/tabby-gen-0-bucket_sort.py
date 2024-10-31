def bucket_sort(my_list: list, bucket_count: int = 10) -> list:
    if len(my_list) == 0 or bucket_count <= 0:
        return []

    min_value, max_value = min(my_list), max(my_list)
    bucket_size = (max_value - min_value) / bucket_count
    buckets: list[list] = [[] for _ in range(bucket_count)]

    for val in my_list:
        index = min(int((val - min_value) / bucket_size), bucket_count - 1)
        buckets[index].append(val)

    return buckets