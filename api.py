import json
from requests import get

# this is a minimised version derived from: https://github.com/itssme/python_pr0gramm_api


class ApiItem(dict):
    def __init__(self, json_str="", json_obj=None):
        if json_str:
            super(ApiItem, self).__init__(json.loads(json_str))

        elif json_obj is not None:
            super(ApiItem, self).__init__(json_obj)

    # override print and to str because json uses " and not ' to represent strings
    def __repr__(self):
        return self.to_json()

    def __str__(self):
        return self.to_json()

    def to_json(self):
        return json.dumps(self)


class Post(ApiItem):
    def __init__(self, json_str="", json_obj=""):
        super(Post, self).__init__(json_str, json_obj)


class Posts(list):
    def __init__(self, json_str=""):
        super(Posts, self).__init__()

        if json_str != "":
            self.json = json.loads(json_str)
            items = self.json["items"]

            for i in range(0, len(items)):
                self.append(Post(json_obj=items[i]))

    def minId(self):
        min = self[0]["id"]
        for elem in self:
            if min > elem["id"]:
                min = elem["id"]
        return min

    def maxId(self):
        max = self[0]["id"]
        for elem in self:
            if max < elem["id"]:
                max = elem["id"]
        return max


class Api:
    def __init__(self, username="", password="", tmp_dir="./"):
        self.__password = password
        self.__username = username
        self.__login_cookie = None
        self.__current = -1

        self.tmp_dir = tmp_dir

        self.image_url = 'https://img.pr0gramm.com/'
        self.api_url = 'https://pr0gramm.com/api/'
        self.login_url = 'https://pr0gramm.com/api/user/login/'
        self.profile_comments = self.api_url + "profile/comments"
        self.profile_user = self.api_url + "profile/info"
        self.items_url = self.api_url + 'items/get'
        self.item_url = self.api_url + 'items/info'

        self.logged_in = False

    @staticmethod
    def calculate_flag(sfw=True, nsfp=False, nsfw=False, nsfl=False):
        """
        Used to calculate flags for the post requests

        sfw = 1
        nsfw = 2
        sfw + nsfw = 3
        nsfl = 4
        nsfw + nsfl = 6
        sfw + nsfw + nsfl = 7
        nsfp = 8
        sfw + nsfp = 9
        sfw + nsfp + nsfw = 11
        sfw + nsfp + nsfw + nsfl = 15
        
        :param sfw: bool
        :param nsfp: bool
        :param nsfw: bool
        :param nsfl: bool
        :return: Calculated flag for requests
        """
        flag = 0

        flag += 1 if sfw else 0
        flag += 2 if nsfw else 0
        flag += 4 if nsfl else 0
        flag += 8 if nsfp and sfw else 0

        return flag

    def get_newest_image(self, flag=1, promoted=0, user=None):
        """
        Gets the newest post either on /new (promoted=0) or /top (promoted=1)
        Parameters
        ----------
        :param flag: int or str
                     see api.md for details
                     call calculate_flag if you are not sure what flag to use
        :param promoted: int (0 or 1)
                         0 for all posts
                         1 for posts that have been in top
        :param user: str
                     get uploads from one specific user
        :return: str
                 json reply from api
        """
        if user is None:
            r = get(self.items_url,
                    params={'flags': flag, 'promoted': promoted},
                    cookies=self.__login_cookie)
        else:
            r = get(self.items_url,
                    params={'flags': flag, 'promoted': promoted, 'user': user},
                    cookies=self.__login_cookie)
        r = r.content.decode("utf8")
        r = json.dumps(json.loads(r)["items"][0])
        return r

    def get_items_by_tag(self, tags, flag=1, older=-1, newer=-1, promoted=0, user=None):
        """
        Gets items with a specific tag from the pr0gramm api

        Parameters
        ----------
        :param tags: str
                     Search posts by tags
                     Example: 'schmuserkadser blus'
                               Will return all posts with the tags
                               'schmuserkadser' and 'blus'
        :param flag: int or str
                     see api.md for details
                     call calculate_flag if you are not sure what flag to use
        :param older: int
                      Specifies the first post that will be returned from the api
                      For example: older=2525097 tags='schmuserkadser' will get
                                   the post '2525097' and all posts after that with the specified tag
        :param newer: int
                      Specifies the first post that will be returned from the api
                        For example: older=2525097 tags='schmuserkadser' will get
                                   the post '2525097' and all posts newer than '2525097' with the specified tag
        :param promoted: int 0 or 1
                         0 for all posts
                         1 for posts that have been in top
        :param user: str
                     get uploads from one specific user
        :return: str
                 json reply from api
        """

        if older != -1:
            params = {'older': older, 'flags': flag, 'promoted': promoted, 'tags': tags}
        elif newer != -1:
            params = {'newer': newer, 'flags': flag, 'promoted': promoted, 'tags': tags}
        else:
            params = {'flags': flag, 'promoted': promoted, 'tags': tags}
        if user is not None:
            params["user"] = user

        r = get(self.items_url,
                params=params,
                cookies=self.__login_cookie)
        print(r.url)

        return r.content.decode('utf-8')

    def get_items_by_tag_iterator(self, tags, flag=1, older=-1, newer=-1, promoted=0, user=None):
        class __items_tag_iterator:
            self.__current = -1

            def __init__(self, tags, api, flag=1, older=0, promoted=0, user=None):
                self.tags = tags
                self.api = api
                self.flag = flag
                self.older = older
                self.newer = newer
                self.promoted = promoted
                self.user = user

            def __iter__(self):
                if older != -1:
                    self.__current = older
                elif newer != -1:
                    self.__current = newer
                else:
                    self.__current = Post(self.api.get_items_by_tag(self.tags, self.flag, self.older, self.promoted,
                                                                    self.user))
                    self.older = 1

                return self

            def __next__(self):
                posts = Posts(self.api.get_items_by_tag(self.tags, flag=self.flag, newer=self.__current,
                                                        promoted=self.promoted, user=self.user))
                if older != -1:
                    try:
                        self.__current = posts.minId()
                    except IndexError:
                        raise StopIteration
                else:
                    try:
                        self.__current = posts.maxId()
                    except IndexError:
                        raise StopIteration
                return posts

        return __items_tag_iterator(tags, self, flag, older, promoted, user)

    def get_item_info(self, item, flag=1):
        """
        Get item info from pr0gramm api
        For example:
          'https://pr0gramm.com/api/items/info?itemId=2525097'

        Will return all comments and tags for the specified post

        Parameters
        ----------
        :param item: int or str
                     requested post for example: 2525097
        :param flag: int or str
                     see api.md for details
                     call calculate_flag if you are not sure what flag to use
        :return: str
                 json reply from api
        """

        r = get(self.item_url + "?itemId=" + str(item),
                params={'flags': flag},
                cookies=self.__login_cookie)
        return r.content.decode("utf-8")
