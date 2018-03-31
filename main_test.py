from config import token, d, user_dict_update, state, board_field_dict, category_field, filter_state, main_dict
import telebot
from telebot import types
from classes import Users_board
import time
# Обычный режим
token
bot = telebot.TeleBot(token, threaded=False)
user_dict = user_dict_update.copy()
users_id_dict = {}
users_board_dict = {}

user_state = {}


def printf(message):
    print(message.chat.id, "   user_dict     ", users_id_dict[message.chat.id])
    print(message.chat.id, "   user_state    ", user_state[message.chat.id])


def update_user_dict(message):
    users_id_dict[message.chat.id] = user_dict_update.copy()
 

# def local_keyboard(def_value, *dict_key):
#     print(dict_key, def_value)
#     user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
#     if len(dict_key) == 1:
#         for key in d[dict_key[0]]:
#             user_markup.row(key)
#     if len(dict_key) == 2:
#         for key in d[dict_key[1]]:
#             user_markup.row(key)
#     if len(dict_key) == 3:
#         for key in d[dict_key[1]][dict_key[2]]:
#             user_markup.row(key)
#     if len(dict_key) > 1:
#         user_markup.row(dict_key[0])
#     if def_value:
#         user_markup.row(def_value)
#     return user_markup



def get_current_state(user_id):
    if user_id in user_state:
        return user_state[user_id]
    else:
        set_state(user_id, "start")
        return user_state[user_id]

def get_name_state(c_state):
    for item in state:
        if state[item] == c_state:
            return item

def set_state(user_id, state_user):
    print(state_user)
    print(state[state_user])
    user_state[user_id] = state[state_user]

def html_board(user_object, inline_key="right"):
    list_db = user_object.list_from_db
    list_db
    if list_db:
        marker = user_object.marker
        step = 1
        if inline_key == "right":
            if marker + 5 >= len(list_db):
                marker_end = len(list_db) - 1
            else:
                marker_end = marker + 5
        elif inline_key == "left":
            step = -1
            if marker - 5 < 0:
                marker_end = 0
            else:
                marker_end = marker - 5
        user_object.marker = marker_end
        html_code = ""
        if marker == marker_end:
            return "Показаны все объявления, или листайте в другую сторону"
        html_code += "*" + str(category_field[list_db[0]['category_id']]) + "*"
        for key in list_db[marker:marker_end:step]:
            print("++++++++++++++++++++++++++")
            print(key)
            print(list_db.index(key))
            # html_code += "\n\n*" + str("Заголовок") + ": *[" + \
            html_code += "\n\n[" + \
                         str(key["title"]) + "](https://ekoplod.ru/board/" + str(key["slug"] + ".html") +")"
            for field in board_field_dict:
                if key[field]:
                    if field == "date_pub":
                        key[field] = str(key[field])[:11]
                    if field == "blood":
                        print(key)
                        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
                        print(key[field])
                        if str(key[field]).isdigit():
                            key[field] = d["filters"]["Группа крови"][key[field]-1]
                    if field == "content":
                        if len(key[field]) > 350:
                            key[field] = key[field][:340] + ". . .\n" + "_Продолжение можно прочитать по_ [ссылке]"+"(" + "https://ekoplod.ru/board/" + str(key["slug"] + ".html") +")"
                    html_code += "\n*" + str(board_field_dict[field]) + ": *" +\
                                 str(key[field])
        html_code += "\n" + "_" + "Показаны " + str(min(marker,marker_end)+1) + " - " + str(max(marker,marker_end))\
                        + " объявления из " + str(len(list_db)-1) + "_"
        print(html_code)
        return html_code
    else:
        return ("Объявлений с такими парметрами нет")


def inline_left_right(page_left=0, page_right=0):
    keyboard = types.InlineKeyboardMarkup()
    url_button_right = types.InlineKeyboardButton(text="➡️", callback_data="right")
    url_button_left = types.InlineKeyboardButton(text="⬅️",  callback_data="left")
    keyboard.add(url_button_left, url_button_right)
    return keyboard


def display_dict(message, list_from_db):
    user_object = Users_board()
    user_object.list_from_db = list_from_db
    user_object.message_board_id = message.message_id + 1
    users_board_dict.update({message.from_user.id: user_object})
    text_m = html_board(user_object)
    bot.send_message(message.from_user.id, text_m, parse_mode="Markdown", disable_web_page_preview=True, reply_markup=inline_left_right())

def main_keyboad(dict_key, back_key = None):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    for item in main_dict[dict_key]:
        user_markup.row(item)
    if back_key:
        user_markup.row(back_key)
    return user_markup
    
@bot.message_handler(func=lambda message: not(message.chat.id in user_state))
def user_start(message):
    if message.text in main_dict["start"]:
        users_id_dict.update({message.chat.id: user_dict_update.copy()})
        users_id_dict[message.chat.id]["start"] = message.text
        bot.send_message(message.chat.id,
                         "Теперь выберите категорию",
                         reply_markup=main_keyboad("category", "Назад"))
        set_state(message.chat.id, "category")
    else:
        bot.send_message(message.chat.id,
                        "Выберите действие",
                        reply_markup=main_keyboad("start"))
        set_state(message.chat.id, "start")
        users_id_dict.update({message.chat.id: user_dict_update.copy()})


   
@bot.message_handler(func=lambda message: get_current_state(message.chat.id) == state["start"])
def user_entering_start(message):
    if message.text in main_dict["start"]:
        users_id_dict[message.chat.id]["start"] = message.text
        bot.send_message(message.chat.id,
                         "Теперь выберите категорию",
                         reply_markup=main_keyboad("category", "Назад"))
        set_state(message.chat.id, "category")
    else:
        bot.send_message(message.chat.id,
                         "Выберите действие",
                         reply_markup=main_keyboad("start"))
    printf(message)

def user_filters_keyboard(user_id):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    value = ": "
    dict_key = {}
    for key in users_id_dict[user_id]:
        if (key != "start") and (key != "category"):
            if len(users_id_dict[user_id][key]) == 1:
                value += str(users_id_dict[user_id][key][0])
            elif len(users_id_dict[user_id][key]) == 2:
                value += (str(users_id_dict[user_id][key][0]))+("-")+(str(users_id_dict[user_id][key][1]))
            else:
                value += "не важно"
            dict_key.update({key:str(key+value)})
            value = ": "
    print(dict_key)
    user_markup.row(dict_key["Вес"],dict_key["Возраст"])
    user_markup.row(dict_key["Рост"], dict_key["Дети"])
    user_markup.row(dict_key["Группа крови"])
    user_markup.row(dict_key["Город"])
    user_markup.row("Применить фильтры", "Вернуться к категориям")
    return user_markup

@bot.message_handler(func=lambda message: get_current_state(message.chat.id) == state["category"])
def user_entering_category(message):
    if message.text in main_dict["category"]:
        users_id_dict[message.chat.id]["category"] = message.text
        bot.send_message(message.chat.id,
                         "Нажмите на пункт, чтобы изменить, или нажмите готово",
                         reply_markup=user_filters_keyboard(message.chat.id))
        set_state(message.chat.id, "filters")
    elif message.text == "Назад":
        bot.send_message(message.chat.id,
                     "Выберите действие",
                     reply_markup=main_keyboad("start"))
        set_state(message.chat.id, "start")
        users_id_dict.update({message.chat.id: user_dict_update.copy()})
    else:
        bot.send_message(message.chat.id,
                         "Теперь нужно выбрать категорию",
                         reply_markup=main_keyboad("category", "Назад"))
    printf(message)

def local_filter_keyboard(keyboard):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    if keyboard:
        if len(keyboard) % 2 == 0:
            index = 0
            while index <= len(keyboard) - 2:
                user_markup.row(keyboard[index], keyboard[index+1])
                index += 2
        else:
            for item in keyboard:
                user_markup.row(item)

    user_markup.row("Оставить пустым", "Назад")
    return(user_markup)

def choose_state(text, filter_dict):
    for item in filter_dict:
        if text in filter_dict[item]:
            return item

 

def send_entering_filter(message):
    filter_dict =  main_dict["filter"]
    chosen_state = choose_state(message.text, filter_dict)
    bot.send_message(message.from_user.id, filter_dict[chosen_state][2], 
                     reply_markup=local_filter_keyboard(filter_dict[chosen_state][3]))
    set_state(message.chat.id, chosen_state)
    printf(message)

@bot.message_handler(func=lambda message: get_current_state(message.chat.id) == state["filters"])
def user_entering_filters(message):
    message.text = message.text.split(":")[0]
    filters_list = [main_dict["filter"][item][1] for item in main_dict["filter"]]
    if message.text in filters_list:
        send_entering_filter(message)
    elif message.text == "Применить фильтры":
        from classes import DataBase
        date_b = DataBase()
        display_dict(message, date_b.get_ankets_list(users_id_dict[message.chat.id]))
        set_state(message.chat.id, "ready")
    elif message.text == "Вернуться к категориям":
        bot.send_message(message.chat.id,
                         "Выберите категорию",
                         reply_markup=main_keyboad("category", "Назад"))
        set_state(message.chat.id, "category")
    else:
        bot.send_message(message.chat.id, "Нажмите на пункт, чтобы изменить, или нажмите применить фильтры",
                         reply_markup=user_filters_keyboard(message.from_user.id))
        set_state(message.chat.id, "filters")


@bot.message_handler(func=lambda message: get_current_state(message.chat.id) in filter_state)
def user_entering_filter(message):
    filter_dict =  main_dict["filter"]
    chosen_state = choose_state(message.text, filter_dict)
    def return_to_filters(message):
        bot.send_message(message.chat.id, "Нажмите на пункт, чтобы изменить, или нажмите применить фильтры",
                         reply_markup=user_filters_keyboard(message.from_user.id))
        set_state(message.chat.id, "filters")
    import re
    cs = get_current_state(message.chat.id)
    if cs == 4:
        result = re.match(r'\s*[0-9][0-9]\s*-\s*[0-9][0-9]\s*', message.text)
        if result and (len(result.group(0)) == len(message.text)):
            age_list = list(map(int, result.group(0).split("-")))
            age_list.sort()
            users_id_dict[message.chat.id]["Возраст"] = list(map(str, age_list))
            printf(message)
            return_to_filters(message)
        elif message.text == "Назад":
            return_to_filters(message)
        elif message.text == "Оставить пустым":
            users_id_dict[message.chat.id]["Возраст"] = []
            return_to_filters(message)
        else:
            bot.send_message(message.chat.id, "Возраст введен не коректно, пожалуйста попробуйте еще раз.\nПример: 25-37",
                             reply_markup=local_filter_keyboard(filter_dict[get_name_state(cs)][3]))
    elif cs == 5:
        result = re.match(r'\s*[1-2][0-9][0-9]\s*-\s*[1-2][0-9][0-9]\s*', message.text)
        if result and (len(result.group(0)) == len(message.text)):
            height_list = list(map(int, result.group(0).split("-")))
            height_list.sort()
            print(height_list)
            users_id_dict[message.chat.id]["Рост"] = list(map(str, height_list))
            return_to_filters(message)
        elif message.text == "Назад":
            return_to_filters(message)
        elif message.text == "Оставить пустым":
            users_id_dict[message.chat.id]["Рост"] = []
            return_to_filters(message)
        else:
            bot.send_message(message.chat.id, "Рост введен не коректно, пожалуйста попробуйте еще раз.\nПример: 160-170",
                             reply_markup=local_filter_keyboard(filter_dict[get_name_state(cs)][3]))
    elif cs == 6:
        result = re.match(r'\s*[1-2]?[0-9][0-9]\s*-\s*[1-2]?[0-9][0-9]\s*', message.text)
        if result and (len(result.group(0)) == len(message.text)):
            weight_list = list(map(int, result.group(0).split("-")))
            weight_list.sort()
            print(weight_list)
            users_id_dict[message.chat.id]["Вес"] = list(map(str, weight_list))
            return_to_filters(message)
        elif message.text == "Назад":
            return_to_filters(message)
        elif message.text == "Оставить пустым":
            users_id_dict[message.chat.id]["Вес"] = []
            return_to_filters(message)
        else:
            bot.send_message(message.chat.id, "Вес введен не коректно, пожалуйста попробуйте еще раз.\nПример: 75-120",
                             reply_markup=local_filter_keyboard(filter_dict[get_name_state(cs)][3]))
    elif cs == 7:
        if message.text in main_dict["filter"]["child"][3]:
            users_id_dict[message.chat.id]["Дети"] = [message.text]
            return_to_filters(message)
        elif message.text == "Назад":
            return_to_filters(message)
        elif message.text == "Оставить пустым":
            users_id_dict[message.chat.id]["Дети"] = []
            return_to_filters(message)
        else:
            bot.send_message(message.chat.id, "Пожалуйста, выберите один из пунктов",
                             reply_markup=local_filter_keyboard(filter_dict[get_name_state(cs)][3]))
    elif cs == 8:
        if message.text in  main_dict["filter"]["blood"][3]:
            # подгоняем под базу данных в индексах группу крови
            users_id_dict[message.chat.id]["Группа крови"] = [message.text]
            return_to_filters(message)
        elif message.text == "Назад":
            return_to_filters(message)
        elif message.text == "Оставить пустым":
            users_id_dict[message.chat.id]["Группа крови"] = []
            return_to_filters(message)
        else:
            bot.send_message(message.chat.id, "Пожалуйста, выберите один из пунктов",
                            reply_markup=local_filter_keyboard(filter_dict[get_name_state(cs)][3]))
    elif cs == 9:
        if not(message.text == "Назад") and not(message.text == "Оставить пустым"):
            users_id_dict[message.chat.id]["Город"] = [message.text]
            return_to_filters(message)
        elif message.text == "Назад":
            return_to_filters(message)
        elif message.text == "Оставить пустым":
            users_id_dict[message.chat.id]["Город"] = []
            return_to_filters(message)
        else:
            bot.send_message(message.chat.id, "Пожалуйста, выберите один из пунктов",
                             reply_markup=local_filter_keyboard(filter_dict[get_name_state(cs)][3]))
    printf(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message and call.from_user.id in users_board_dict:
        if call.data == "right":
                text_m = html_board(users_board_dict[call.from_user.id], inline_key="right")
                bot.edit_message_text(chat_id=call.message.chat.id, disable_web_page_preview=True, message_id=call.message.message_id, text=text_m, parse_mode="Markdown", reply_markup=inline_left_right()    )
        elif call.data == "left":
                text_m = html_board(users_board_dict[call.from_user.id], inline_key="left")
                bot.edit_message_text(chat_id=call.message.chat.id, disable_web_page_preview=True, message_id=call.message.message_id, text=text_m, parse_mode="Markdown", reply_markup=inline_left_right())


@bot.message_handler(func=lambda message: get_current_state(message.chat.id) == state["ready"])
def new_iter(message):
    if message.text == "Сбросить фильтры":
        for item in users_id_dict[message.chat.id]:
            if item != "start" and item != "category":
                users_id_dict[message.chat.id][item] = []
        bot.send_message(message.chat.id,
                         "Нажмите на пункт, чтобы изменить, или нажмите готово",
                         reply_markup=user_filters_keyboard(message.chat.id))
        set_state(message.chat.id, "filters")
    elif message.text == "Вернуться к категориям":
        bot.send_message(message.chat.id,
                         "Выберите категорию",
                         reply_markup=main_keyboad("category", "Назад"))
        set_state(message.chat.id, "category")
    elif message.text == "Сбросить все":
        set_state(message.chat.id, "start")
        update_user_dict(message)
        bot.delete_message(chat_id=message.chat.id, message_id=users_board_dict[message.chat.id].message_board_id)
        bot.send_message(message.chat.id,
                        "Выберите действие",
                        reply_markup=main_keyboad("start"))
    else:
        bot.send_message(message.chat.id,
                        "Выберите действие",
                        reply_markup=main_keyboad("ready")) 
    
    


while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        print("Ошибка: ",e)
        import traceback
        traceback.print_exc()  # или просто print(e) если у вас логгера нет,
        # или import traceback; traceback.print_exc() для печати полной инфы
        time.sleep(15)
