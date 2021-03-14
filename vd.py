from requests import get as reqget
from time import sleep, ctime
from random import choices

ua = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}

# Генератор рандомной строки для лога с ошибками
def genrand():
    return "".join(choices("abcdefghijklmnopqrstuvwxyz", k=6))

# Отдельный обработчик ошибок для send_message, имхо их слишком много, чтобы обрабатывать их всех в одной функции
def smhandler(errorcode):
    verdict = ""
    if errorcode == 5:
        verdict = "Токен недействительный! Возможно, владелец аккаунта сменил пароль."
    if errorcode == 6:
        verdict = "Вы слишком часто отправляете сообщения!"
    elif errorcode == 15:
        verdict = "Доступ к функции запрещен, свяжитесь с разработчиком!"
    elif errorcode == 900:
        verdict = "Нельзя отправлять сообщение пользователю из чёрного списка!"
    elif errorcode == 902:
        verdict = "Пользователь ограничил отправку ему сообщений от вашего аккаунта!"
    elif errorcode == 914:
        verdict = "Сообщение слишком длинное!"
    elif errorcode == 917:
        verdict = "У вас нет доступа к этому чату, возможно вас забанили!"
    elif errorcode == 945:
        verdict = "Этот чат закрыт!"
    elif errorcode == 950:
        verdict = "Вы слишком часто отправляете сообщения!"
    else:
        filename = f"log_{genrand()}.txt"
        with open(filename, "w") as f:
            f.write(resp)
            f.close()
        verdict = f"Произошла неизвестная ошибка, отправьте лог {filename} разработчику!"
    return verdict

# Проверка валидности токена
def check_valid(token):
    resp = reqget(f"https://api.vk.com/methods/users.get?access_token={token}&v=5.130", headers=ua)
    print(resp)
    print(resp.text)
    resp = resp.json()
    if resp.get("response") is None:
    	print("Токен невалидный!")
    	exit()

# Получение диалогов и их показ
def show_dialogs(token):
    dialogs = {}
    resp = reqget(f"https://api.vk.com/methods/messages.getConversations?access_token={token}&count=200&v=5.130", headers=ua).json()
    if resp.get("response") is None:
        errorcode = resp["error"]["error_code"]
        if errorcode == 5:
            print("Произошла ошибка: токен недействительный! Возможно, владелец аккаунта сменил пароль.")
        else:
            filename = f"log_{genrand()}.txt"
            with open(filename, "w") as f:
                f.write(resp)
                f.close()
            print(f"Произошла неизвестная ошибка, отправьте лог {filename} разработчику!")
        return
    for i in resp["response"]["items"]:
        userid = str(i["peer"]["id"])
        while True:
            try:
                respp = reqget(f"https://api.vk.com/methods/users.get?access_token={token}&user_ids={userid}&v=5.130", headers=ua).json()["response"][0]
                user_name = "{} {}".format(respp["first_name"], respp["last_name"])
                break
            except:
                sleep(5)
        dialogs.append({"id": userid, "name": user_name})
        dialogs.reverse()
        for i in dialogs:
            print("{} - {}".format(i["id"], i["name"]))

# Вызов сообщений, их сортировка и показ
def show_messages(token, userid):
    resp = reqget(f"https://api.vk.com/methods/messages.getHistory?access_token={token}&user_id={userid}&count=200&v=5.130", headers=ua).json()
    if resp.get["response"] is None:
        errorcode = resp["error"]["error_code"]
        if errorcode == 5:
            print("Произошла ошибка: токен недействительный! Возможно, владелец аккаунта сменил пароль.")
        elif errorcode == 100:
            print("Произошла ошибка: такого пользователя не существует!")
        else:
            print("Произошла неизвестная ошибка! Попробуйте позже.")
        return
    msgslist = resp["response"]["items"]
    if msglist == []:
        print("У владельца токена нет диалога с этим пользователем!")
        return
    messages = []
    for i in msglist:
        messages.append({"sender": str(i["from_id"]), "date": ctime(i["date"]), "text": i["text"]})
    messages.reverse()
    for i in messages: # вроде костыль, но я иначе не придумал, они в перевернутом виде возвращаются апишкой. если есть способ реализовать лучше - напишите 
        print("[{}] {} - {}".format(i["date"], i["sender"], i["text"]))

# Отправка сообщения
def send_message(token, userid, message):
    resp = reqget(f"https://api.vk.com/methods/messages.send?access_token={token}&user_id={userid}&random_id=0&message={message}&v=5.130", headers=ua).json()
    if resp.get("response") is None:
        errordesc = smhandler(resp["error"]["error_code"])
        print(f"Произошла ошибка: {errordesc}")
        return
    print("Сообщение отправлено!")


if __name__ == "__main__":

    print("VKDialoger by ratabomb for @tg_inc_soft")
    token = input("Введите ваш токен: ")

    print("Подключаемся к VK API...")
    check_valid(token)

    while True:
        print("\n-----------\nВыберите действие:\n1 - Показать диалоги\n2 - Показать сообщения в диалоге\n3 - Отправить сообщение\n")
        ch = str(input(">>> "))
        if ch == "1":
            show_dialogs(token)
        elif ch == "2":
            userid = str(input("Введите user id человека, диалог с которым вы хотите посмотреть: "))
            show_messages(token, userid)
        elif ch == "3":
            userid = str(input("Введите user id человека, которому вы хотите отправить сообщение: "))
            message = str(input("Введите сообщение: "))
            send_message(token, userid, message)
        else:
            print("Такого действия нет!")