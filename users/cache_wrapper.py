from django.core.cache import cache

WEEK_IN_SEC = 604800


def cache_w_add(relatedTo, id, typeOfInfo, data, ttl):

    num_info = relatedTo + ":" + str(id) + ":" + typeOfInfo
    if num_info not in cache:
        cache.set(num_info, 0)

    id_info = cache.incr(num_info)

    cache.set(num_info + ":" + str(id_info), data, ttl)
    return num_info


def cache_w_gets(relatedTo, id, typeOfInfo):
    key_all = relatedTo + ":" + str(id) + ":" + typeOfInfo + ":*"
    cacheValues = []
    for info in cache.iter_keys(key_all):
        tmp = cache.get(info)
        tmp['id_cache'] = info[-1]
        cacheValues.append(tmp)
    return cacheValues

def cache_w_get(relatedTo, id, typeOfInfo, id_info):
    key = relatedTo + ":" + str(id) + ":" + typeOfInfo + ":" + str(id_info)
    return cache.get(key)


def cache_w_delete(relatedTo, id, typeOfInfo, id_info):
    key = relatedTo + ":" + str(id) + ":" + typeOfInfo + ":" + str(id_info)
    cache.delete(key)

def cache_w_deletes(relatedTo, id, typeOfInfo):
    key = relatedTo + ":" + str(id) + ":" + typeOfInfo + ":*"
    cache.delete_pattern(key)
