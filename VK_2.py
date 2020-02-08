import requests
import networkx as nx

api_url = 'https://api.vk.com/method/'
user_id_1 = 162425
user_id_2 = 58482966
v = '5.103'
access_token = 'b5f7e866b5f7e866b5f7e8660db59862bdbb5f7b5f7e866ebcc094c6e906cd84e33e0e7'
vk = nx.DiGraph()


def get_friends(user_id):
    try:
        friends = requests.get(f'{api_url}friends.get?user_id={user_id}&v={v}&access_token={access_token}').json()
        list_id = friends['response']['items']
    except Exception as e:
        return None
    return list_id


def add_graf(user, list):
    for lis in list:
        vk.add_edge(user, lis, weight=1)
        vk.add_edge(lis, user, weight=1)


def find_result():
    try:
        result = nx.shortest_path(vk, user_id_1, user_id_2)
    except Exception as e:
        result = None
        return result
    else:
        return result


def get_friends_all(user_list):
    new_page = []
    for user in user_list:
        pages = get_friends(user)
        if pages == None:
            pass
        else:
            add_graf(user, pages)
            for page in pages:
                new_page.append(page)
        if find_result() != None:
            return None, find_result()
            break
        else:
            res = None
    return new_page, res


if __name__ == '__main__':
    pages_start = get_friends(user_id_1)
    add_graf(user_id_1, pages_start)
    pages_finish = get_friends(user_id_2)
    add_graf(user_id_2, pages_finish)
    res = find_result()
    if res != None:
        print(res)
    else:
        while res == None:
            pages_start, res = get_friends_all(pages_start)
            pages_finish, res = get_friends_all(pages_finish)
    print(res)

