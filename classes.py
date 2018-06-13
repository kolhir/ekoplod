import telebot
import config
import time

dict_conformity = {"Ищут": {
                            "Суррогатные мамы":"23",
                            "Доноры ооцитов": "20",
                            "Доноры спермы": "15",
                            },
                   "Хотят стать" : {
                                   "Суррогатные мамы":"22",
                                   "Доноры ооцитов": "19",
                                   "Доноры спермы": "16"
                                   },
                    "Возраст": "price",
                    "Вес": "weight",
                    "Рост": "height",
                    "Дети": "children",
                    "Группа крови": "blood",
                    "Город":  "city"
                   }
d = {"start": ["Ищут", "Хотят стать"],
     "category": ["Суррогатные мамы",
                  "Доноры ооцитов",
                  "Доноры спермы"],
     "filters": {"Возраст": [],
                 "Вес": [],
                 "Рост": [],
                 "Дети": ["Есть", "Нет"],
                 "Группа крови": ["O(I) Rh-" ,
                                  "O(I) Rh+",
                                  "A(II) Rh-",
                                  "A(II) Rh+",
                                  "B(III) Rh−",
                                  "B(III) Rh+",
                                  "AB(IV) Rh-",
                                  "AB(IV) Rh+"],
                 "Город": []}}

user_dict = {"start": "",
             "category": "",
             "Возраст": [],
             "Вес": [],
             "Рост": [],
             "Дети": [],
             "Группа крови": [],
             "Город":  []}


class DataBase():
    def get_ankets_list(self, user_dict):
        import pymysql
        user_dict = user_dict.copy()
        start = user_dict["start"]
        category = user_dict["category"]
        category_id = dict_conformity[start][category]
        kwargs = {}

        for key in user_dict:
            if user_dict[key] and (isinstance(user_dict[key], list)):
                if key == "Группа крови":
                    # подгоняем под базу данных в индексах группу крови
                    user_dict[key] = [d["filters"]["Группа крови"].index(user_dict[key][0])+1]
                elif key == "дети":
                    user_dict[key] = ([1] if user_dict[key][0] == "Есть" else [0])

                kwargs.update({key: user_dict[key]})

        db = pymysql.connect(host='178.57.222.29',
                             user='vilyachk_ekoplod',
                             password='rQLcaxs2',
                             db='vilyachk_ekoplod',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

        cursor = db.cursor()
        sqlstr = "SELECT * FROM `cms_con_board` WHERE `category_id`="+category_id+""
        for args in kwargs:
            print(kwargs[args])
            if args == "Группа крови":
                sqlstr += (" AND `" + dict_conformity[args] + "`"
                           + "=" + str(kwargs[args][0]))
            elif args == "Дети":
                if kwargs[args][0] == 0:
                    sqlstr += (" AND " + dict_conformity[args] + " IS NULL ")
            elif len(kwargs[args]) == 1:
                sqlstr += (" AND `" + dict_conformity[args] + "`"
                           + "=" + "\'" + str(kwargs[args][0]) + "\' ")
            elif len(kwargs[args]) == 2:
                sqlstr += (" AND `" + dict_conformity[args] + "`"
                           + " BETWEEN "
                           + str(kwargs[args][0])
                           + " AND "
                           + str(kwargs[args][1])
                            )
        sqlstr += " ORDER BY `cms_con_board`.`date_pub` DESC "
        print(sqlstr)
        cursor.execute(sqlstr)
        k = cursor.fetchall()
        db.close()
        new_list = []
        for item in k:
            # print(item)
            # print(item["date_approved"])
            if item["is_pub"] == 1:
                new_list.append(item)
        return new_list


class Users_board():
    def __init__(self):
        self.marker = 0
        self.list_from_db = []
        self.message_board_id = None


class Bot():

    def __init__(self):
        token = config.token
        self.bot = telebot.TeleBot(token, threaded=False)
        self.markup = Markup()
        self.user = {}

    def get_message(self):
        def start(message):
            self.bot.send_message(message.from_user.id,
                                  "Выбери действие",
                                  reply_markup=self.markup.get(
                                                keyboard="start"))

        def category(message):
            self.bot.send_message(message.from_user.id,
                                  "Выбери подкатегорию",
                                  reply_markup=self.markup.get(
                                                keyboard="category"))

        def filter(message):
            if not(message.from_user.id in self.user_filter):
                self.user_filter.update({message.from_user.id: UsersRequest()})

        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            if not(message.from_user.id in self.user_filter):
                self.user_filter.update({message.from_user.id: UsersRequest()})

            start(message)

        @self.bot.message_handler(content_types=['text'])
        def handle_text(message):
            u_id = message.from_user.id
            if u_id in self.user_filter:
                if len(self.user_filter[u_id]) == 0:
                    if message.text in self.markup.key_dict["start"]:
                        self.user_filter[u_id] = {"start": message.text}
                        category(message)
                    else:
                        start(message)
                elif len(self.user_filter[u_id]) == 1:
                    if message.text in self.markup.key_dict["category"]:
                        self.user_filter[u_id].update({"category": message.text})
                        category(message)
                    else:
                        category(message)
                else:
                    filter(message)
            else:
                self.user_filter[message.from_user.id] = {}
                start(message)
                # if message.text in self.markup.key_dict["start"]:
                #     if message.from_user.id in self.user_filter:
                #         self.user_filter[message.from_user.id] = {"start": message.text}
                #     category(message)
                # elif message.text in self.markup.key_dict["category"]:
                #     if len(self.user_filter) == 1:
                #         self.user_filter[message.from_user.id].update({"category": message.text})
                #     else:
                #         self.user_filter[message.from_user.id] = {}
                #         start(message)
                #     filter(message)
                # else:
                #     start(message)

        while True:
            try:
                self.bot.polling(none_stop=True)

            except Exception as e:
                print("Ошибка: ", e)
                import traceback
                traceback.print_exc()
                time.sleep(15)


class Markup():
    key_dict = {"start": ["Ищу",
                          "Стану"],
                "category": ["Суррогатные мамы",
                             "Доноры ооцитов",
                             "Доноры спермы"],
                "filters": ["Возраст",
                            "Вес",
                            {"Свои дети": ["Есть", "Нет"]},
                            {"Группа крови": ["O(I) Rh-",
                                              "O(I) Rh+",
                                              "A(II) Rh-",
                                              "A(II) Rh+",
                                              "B(III) Rh−",
                                              "B(III) Rh+",
                                              "AB(IV) Rh-",
                                              "AB(IV) Rh+"]},
                            "Город"]}

    def get(self, keyboard):
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)

        for key in self.key_dict[keyboard]:
            user_markup.row(key)

        return user_markup

# from classes import DataBase
# DataBase.get_ankets_list(id = 5)
# DataBase.get_ankets_list(tags = "ищу яйцеклетки")
