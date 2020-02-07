import requests
import copy
import time

headers = {
    'User-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
}

api_url = 'https://api.vk.com/method/'
user_id_1 = 4059151
user_id_2 = 54140617
v = '5.103'
access_token = 'b5f7e866b5f7e866b5f7e8660db59862bdbb5f7b5f7e866ebcc094c6e906cd84e33e0e7'


def compare(friends_list):
    result = ''
    for i in range(len(friends_list)):
        if friends_list[i][-1] == user_id_2:
            result = i
    return result


def get_friends(user_id):
    try:
        friends = requests.get(f'{api_url}friends.get?user_id={user_id}&v={v}&access_token={access_token}').json()
        fr_count = friends['response']['count']
        list_id = friends['response']['items']
    except Exception as e:
        return None
    return list_id


def find_friends(old_base):
    new_base = []
    for i in range(len(old_base)):
        func_base = []
        print(old_base[i][-1])
        time.sleep(0.5)
        lists = get_friends(old_base[i][-1])
        if lists == None:
            pass
        else:
            for j in range(len(lists)):
                new_list = copy.deepcopy(old_base[i])
                new_list.append(lists[j])
                func_base.append(new_list)
                new_base.append(new_list)
            result = compare(func_base)
            if result != '':
                break
    return new_base, result, func_base


base = []
if __name__ == '__main__':
    friends_list = get_friends(user_id_1)
    for i in friends_list:
        list = [user_id_1, i]
        base.append(list)
    result = compare(base)
    if result != '':
        print(base[result])
    else:
        old_base, result, func_base = find_friends(base)
        while result == '':
            old_base, result, func_base = find_friends(old_base)
        else:
            print(func_base[result])
            chain = []
            for url in func_base[result]:
                chain.append(f'https://vk.com/id{url}')
            ruki = {
                'persona_a': f'https://vk.com/id{user_id_1}',
                'persona_b': f'https://vk.com/id{user_id_2}',
                'chain': chain
            }
            print(ruki)
