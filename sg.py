#!/usr/bin/python3
import time
import requests
import random
from bs4 import BeautifulSoup
import os
import json
import re
import datetime
import logging
import util
import steamcn

version = "1.3.0"
os.chdir(os.path.dirname(os.path.realpath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(asctime)s %(message)s'
)
# 屏蔽在Ubuntu中，requests产生的日志。
# Mac上设置level=logging.INFO就不会显示了，ubutnu中必须设置大于WARNING，很奇怪啊。
# BUG FIX https://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
logging.getLogger("requests").setLevel(logging.WARNING)


def check_new_version(ver):
    try:
        if requests.get("https://raw.githubusercontent.com/4815162342lost/steam_gifts_bot/master/version").text.rstrip(
                "\n") == ver:
            logging.info("正在使用最新版的程序，当前版本为：" + version)
        else:
            logging.info(
                "发现新版本！\n访问 https://github.com/4815162342lost/steam_gifts_bot 并升级你的bot")
            logging.info("What's new:")
            logging.info(
                requests.get("https://raw.githubusercontent.com/4815162342lost/steam_gifts_bot/master/whats_new").text)
    except Exception as e:
        logging.error("无法检测新版本. Github 不可用或者没有网络连接！\n" + e)


def get_user_agent():
    """read user agent from user_agent.txt"""
    with open("user_agent.txt") as user_agent_from_file:
        user_agent = user_agent_from_file.readline()
        return user_agent


def get_func_list():
    """Set necessary parameters (what type of the giveaways, need beep or not, debug mode or not, need notify or not)"""
    global need_giveaways_from_banners
    global need_send_notify;
    global need_beep
    global debug_mode;
    global threshold
    global silent_mode_at_night;
    logging.info("获得要请求的地址列表....")
    if settings_list["wishlist"]:
        func_list.append("wishlist")
        logging.info("添加地址：wishlist...")
    if settings_list["steamcn_list"]:
        func_list.append("steamcn_list")
        logging.info("添加蒸汽动力列表....")
    if settings_list["search_list"]:
        func_list.append("search")
        logging.info("添加地址：search...")
    if settings_list["group"]:
        func_list.append("group")
        logging.info("添加地址：group...")
    if settings_list["random_list"]:
        func_list.append("someone")
        logging.info("添加地址：someone...")
    if settings_list["giveaways_from_banners"]:
        need_giveaways_from_banners = 1
    if settings_list["send_notify"]:
        need_send_notify = 1
    if settings_list["beep"]:
        need_beep = 1
    if settings_list["debug_mode"]:
        debug_mode = 1
    threshold = settings_list["threshold"]
    silent_mode_at_night = settings_list["silent_mode_at_night"]


def get_requests(cookie, req_type):
    """get first page"""
    global chose
    if req_type == "wishlist":
        logging.info("请求愿望单列表...")
        page_number = 1
        need_next = True
        while need_next:
            try:
                r = requests.get(
                    "https://www.steamgifts.com/giveaways/search?page=" + str(page_number) + "&type=wishlist",
                    cookies=cookie, headers=headers)
                get_game_links(r)
                need_next = get_next_page(r)
                page_number += 1
            except:
                logging.info("愿望单站点不可用")
                util.take_break(30)
                chose = 0
                break
    elif req_type == "steamcn_list":
        logging.info("请求【蒸汽动力私人邀请】列表...")
        try:
            links = steamcn.get_steamcn_Invite()
            for link in links:
                enter_geaway(link)
        except Exception as err:
            logging.info("获取【蒸汽动力私人邀请】链接异常!!!!!")
            logging.info(err)
            util.take_break(30)
            #chose = 0
    elif req_type == "search":
        logging.info("请求search列表...")
        for current_search in what_search.values():
            logging.info("Search giveaways 包含： " + str(current_search))
            page_number = 1
            need_next = True
            while need_next:
                try:
                    r = requests.get(
                        "https://www.steamgifts.com/giveaways/search?page=" + str(page_number) + "&q=" + str(
                            current_search), cookies=cookie, headers=headers)
                    get_game_links(r)
                    need_next = get_next_page(r)
                    page_number += 1
                    util.take_break(random.randint(3, 7))
                except Exception as e:
                    logging.error("search站点不可用")
                    logging.error(e)
                    chose = 0
                    util.take_break(30)
                    break
            time.sleep(random.randint(8, 39))
    elif req_type == "group":
        logging.info("请求group列表...")
        page_number = 1
        need_next = True
        while need_next:
            try:
                r = requests.get("https://www.steamgifts.com/giveaways/search?page=" + str(page_number) + "&type=group",
                                 cookies=cookie, headers=headers)
                get_game_links(r)
                need_next = get_next_page(r)
                page_number += 1
            except Exception as e:
                logging.error("group站点不可用")
                logging.error(e)
                util.take_break(30)
                chose = 0
                break
    elif req_type == "enteredlist":
        logging.info("请求已经加入的抽奖游戏列表...")
        entered_list = []
        page_number = 1
        while nedd_next_page_for_entered_link:
            try:
                r = requests.get("https://www.steamgifts.com/giveaways/entered/search?page=" + str(page_number),
                                 cookies=cookie, headers=headers)
                entered_list.extend(get_entered_links(r))
                page_number += 1
            except:
                logging.info("entered站点不可用")
                chose = 0
                util.take_break(30)
                break
        return entered_list
    elif req_type == "someone" and int(get_coins(get_requests(cookie, "coins_check"))) > int(threshold):
        logging.info("正在请求giveaways随机列表 ...")
        time.sleep(random.randint(5, 11))
        try:
            r = requests.get("https://www.steamgifts.com/", cookies=cookie, headers=headers)
            get_game_links(r)
        except:
            logging.error("随机站点不可用")
            chose = 0
            util.take_break(30)
    elif req_type == "coins_check":
        try:
            r = requests.get("https://www.steamgifts.com/giveaways/search?type=wishlist", cookies=cookie,
                             headers=headers)
            return r
        except:
            logging.info("站点不可用")
            chose = 0
            util.take_break(30)
            return 0


def get_game_links(requests_result):
    """call enter_geaways and extract link"""
    soup = BeautifulSoup(requests_result.text, "html.parser")
    link = soup.find_all(class_="giveaway__heading__name")
    for get_link in link:
        geaway_link = get_link.get("href")
        if not geaway_link in entered_url:
            if not need_giveaways_from_banners and geaway_link in giveaways_from_banner:
                continue
            entered_url.append(geaway_link)
            geaway_link = "https://www.steamgifts.com" + geaway_link
            logging.info('得到游戏地址：' + geaway_link)
            if geaway_link not in bad_giveaways_link:
                if enter_geaway(geaway_link):
                    break
            else:
                logging.info("url在黑名单列表里. 忽略")


def enter_geaway(geaway_link):
    """enter to geaways"""
    global i_want_to_sleep
    global chose
    bad_counter = 0;
    good_counter = 0
    try:
        r = requests.get(geaway_link, cookies=cookie, headers=headers)
        if r.status_code != 200:
            logging.error(r.status_code)
            logging.error("steam gifts站点错误", "错误代码: " + str(r.status_code))
    except:
        logging.error("异常：站点不可用")
        chose = 0
        util.take_break(300)
        return True
    soup_enter = BeautifulSoup(r.text, "html.parser")
    for bad_word in forbidden_words:
        bad_counter += len(re.findall(bad_word, r.text, flags=re.IGNORECASE))
    if bad_counter > 0:
        for good_word in good_words:
            good_counter += len(re.findall(good_word, r.text, flags=re.IGNORECASE))
        if bad_counter > good_counter:
            logging.warning("这是一个陷阱! 小心! 有人正在破坏脚本...")
            do_beep("bad_words")
            with open("bad_giveaways.txt", "a") as bad_giveaways:
                bad_giveaways.write(geaway_link + "\n")
            return False
        if bad_counter == good_counter:
            logging.info("虚惊一场，一切正常." + str(geaway_link))
    try:
        game = soup_enter.title.string
    except:
        logging.info("异常")
        game = "Unknown 游戏"
    if game in bad_games_name:
        logging.info("不喜欢的游戏！")
        return False
    link = soup_enter.find(class_="sidebar sidebar--wide").form
    if link != None:
        al_link = link.find(class_="sidebar__entry-insert is-hidden")
        if al_link is not None:
            logging.info("已经参加此游戏的抽奖，跳过！")
            util.take_break(random.randint(5, 60))
            return False

        link = link.find_all("input")
        params = {"xsrf_token": link[0].get("value"), "do": "entry_insert", "code": link[2].get("value")}
        try:
            r = requests.post("https://www.steamgifts.com/ajax.php", data=params, cookies=cookie, headers=headers)
            extract_coins = json.loads(r.text)
        except:
            logging.error("异常！站点不可用...")
            chose = 0
            util.take_break(300)
            return True
        # print(r.text)
        if extract_coins["type"] == "success":
            coins = extract_coins["points"]
            logging.info("加入游戏: " + re.sub("[^A-Za-z0-9 +-.,:!()]", "", game).rstrip(" ") + " 的抽奖. 剩余体力: " + coins)
            util.take_break(random.randint(1, 120))
            return False
        elif extract_coins["msg"] == "Not Enough Points":
            coins = get_coins(get_requests(cookie, "coins_check"))
            if coins < 10:
                chose = 0
                i_want_to_sleep = True
                logging.info("没有足够的体力..." + str(geaway_link))
                return True
            else:
                return False
    else:
        link = soup_enter.find(class_="sidebar__error is-disabled")
        if link is None:
            logging.info("未发现不可参加的原因，无效链接....")
            util.take_break(random.randint(5, 60))
            return False
        elif link.get_text() == " Not Enough Points":
            logging.info("没有足够的体力抽奖游戏： " + str(geaway_link))
            util.take_break(random.randint(5, 60))
            if int(get_coins(get_requests(cookie, "coins_check"))) < 10:
                chose = 0
                i_want_to_sleep = True
                return True
        else:
            logging.info("Bot不能加入抽奖，原因：" + link.get_text())
            featured_link = soup_enter.select("div.featured__column span")
            if featured_link is not None:
                util.take_break(random.randint(5, 60))
                return False
            else:
                logging.info("Critical error!")
                with open("errors.txt", "a") as error:
                    error.write(featured_link + "\n")
                do_beep("critical")
                logging.info(featured_link)
                return False
        return False


def get_entered_links(requests_result):
    """Entered giveaway list. ignore it"""
    global nedd_next_page_for_entered_link
    entered_list = []
    try:
        soup = BeautifulSoup(requests_result.text, "html.parser")
        links = soup.find_all(class_="table__row-inner-wrap")
    except:
        return entered_list
    for get_link in links:
        url = get_link.find(class_="table__column__heading").get("href")
        check_geaways_end = get_link.find(class_="table__remove-default is-clickable")
        if check_geaways_end != None:
            entered_list.append(url)
        elif get_link.find(class_="table__column__deleted") != None:
            continue
        else:
            nedd_next_page_for_entered_link = False
            return entered_list
    return entered_list


def get_coins(requests_result):
    """how many coins"""
    try:
        soup = BeautifulSoup(requests_result.text, "html.parser")
        coins = soup.find(class_="nav__points").string
        return coins
    except:
        return 0


def get_next_page(requests):
    """Next page exists?"""
    try:
        if requests.text.find("Next") != -1:
            return True
        else:
            return False
    except:
        return False


def set_notify(head, text):
    # """Set notify. Only on Linux"""
    # if not need_send_notify:
    #    return 0
    try:
        sendurl = 'http://sc.ftqq.com/SCU5209T50ff781c69372d9b370387f5c079be01587ae52428055.send?'
        params = {'text': head, 'desp': text}
        params = requests.parse.urlencode(params)
        requests.request.urlopen(sendurl + params)
    except:
        pass


def work_with_win_file(need_write, count):
    """Function for read drom file or write to file won.txt"""
    with open('won.txt', 'r+') as read_from_file:
        if not need_write:
            count = read_from_file.read()
            read_from_file.close()
            return count
        elif need_write:
            read_from_file.seek(0)
            read_from_file.write(str(count))
            read_from_file.close()


def check_won(count):
    """Check new won giveaway"""
    try:
        r = requests.get("https://www.steamgifts.com/giveaways/search?type=wishlist", cookies=cookie, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser").find(class_="nav__right-container").find_all("a")[1].find(
            class_="nav__notification").string
    except:
        logging.info("没有抽中任何游戏... Luck next time!")
        work_with_win_file(True, 0)
        return 0
    if int(count) < int(soup):
        do_beep("won")
        set_notify("中奖了！！", "steamgifts 抽中游戏了！")
        logging.info("中奖了！！steamgifts 抽中游戏了！")
        work_with_win_file(True, soup)
        return soup
    elif int(count) > int(soup):
        work_with_win_file(True, soup)
        return soup
    return count


def do_beep(reason):
    """do beep with PC speacker. Work only on Linux and requrement motherboard speaker"""
    if not need_beep:
        return 0
    if (datetime.datetime.now().time().hour < 9 or datetime.datetime.now().time().hour > 22) and silent_mode_at_night:
        logging.info("保持安静，现在时间太晚了...")
        return 0


def get_games_from_banners():
    soup = BeautifulSoup(requests.get("https://www.steamgifts.com/", cookies=cookie, headers=headers).text,
                         "html.parser")
    banners = soup.find(class_="pinned-giveaways__inner-wrap pinned-giveaways__inner-wrap--minimized").find_all(
        class_="giveaway__heading__name")
    for games in banners:
        if games not in giveaways_from_banner:
            giveaways_from_banner.append(games.get("href"))
            logging.info("你将永远不会赢得这个游戏： " + str(games.get("href")) + ", 因为你拒绝从banner进行抽奖...")


logging.info("bot开始运行...")
func_list = []
need_giveaways_from_banners = 0
need_send_notify = 0;
threshold = 0;
need_beep = 0;
debug_mode = 0
silent_mode_at_night = 0
check_new_version(version)
chose = 0
random.seed(os.urandom)
headers = json.loads(get_user_agent())
cookie = util.get_from_file("cookie.txt")

# try:
#     r = requests.get("https://www.steamgifts.com/giveaways/search?type=wishlist", cookies=cookie, headers=headers)
# except:
#     set_notify("Cookies过期", "快去更新Cookies")
#     do_beep("coockie_exept")
#     sys.exit(1)

what_search = util.get_from_file("search.txt")
util.take_break(random.randint(2, 10))
coins = get_coins(get_requests(cookie, "coins_check"))
nedd_next_page_for_entered_link = True
entered_url = get_requests(cookie, "enteredlist")
# func_list=("wishlist", "search", "someone")
won_count = work_with_win_file(False, 0)

settings_list = util.get_from_file("settings.txt")
bad_games_name = util.get_from_file("black_list_games_name.txt").values()
bad_giveaways_link = util.get_from_file("bad_giveaways_link.txt").values()
get_func_list()
i_want_to_sleep = False
forbidden_words = (" ban", " fake", " bot", " not enter", " don't enter")
good_words = (" bank", " banan", " both", " band", " banner", " bang")
giveaways_from_banner = []

# if not need_giveaways_from_banners:
#    get_games_from_banners()
# logging.info("总体力:" + str(get_coins(get_requests(cookie, "coins_check"))))
logging.info("Steam gifts bot 启动成功！当前总体力为: " + str(coins))

while True:
    if not need_giveaways_from_banners:
        get_games_from_banners()
    i_want_to_sleep = False
    logging.info("开始请求函数列表，总个数为：" + str(len(func_list)) + "个，当前请求第" + str(chose + 1) + "个，请求的函数为:" + func_list[chose])
    requests_result = get_requests(cookie, func_list[chose])
    chose += 1
    if i_want_to_sleep:
        won_count = check_won(won_count)
        sleep_time = random.randint(1800, 3600)
        coins = get_coins(get_requests(cookie, "coins_check"))
        logging.warning("体力太少了，剩余体力: " + str(coins) + ". 开始进入睡眠，预计睡眠 " + str(sleep_time // 60) + " 分钟.")
        print('---------------------------------------------------------------------')
        time.sleep(sleep_time)
        chose = 0
    if chose == len(func_list):
        won_count = check_won(won_count)
        sleep_time = random.randint(1800, 3600)
        coins = get_coins(get_requests(cookie, "coins_check"))
        logging.info("体力剩余:  " + str(coins) + ". 开始进入睡眠，睡眠时长： " + str(sleep_time // 60) + " 分钟.")
        print('----------------------------------------------------------------------')
        time.sleep(sleep_time)
        chose = 0
