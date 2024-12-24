from io import BytesIO
from PIL import Image
import requests
import re
import json


def get_total_card_number():
    r = requests.get("https://hololive-official-cardgame.com/cardlist/cardsearch/?keyword=&attribute%5B%5D=all&expansion_name=&card_kind%5B%5D=all&rare%5B%5D=all&bloom_level%5B%5D=all&parallel%5B%5D=all")
    # print('requesting for card count ')
    # print('')
    content = r.content.decode('utf-8', 'ignore')

    card_count_rx = "検索結果.*>(\\d+)<.*件"
    m = re.search(card_count_rx, content)

    return int(m.group(1))


cards = {}

total_cards = get_total_card_number()
print(f"found {total_cards} total cards")


def get_card_from_official_site(id):

    base = 'https://hololive-official-cardgame.com/cardlist/?id={id}&keyword=&attribute%5B0%5D=all&expansion_name=&card_kind%5B0%5D=all&rare%5B0%5D=all&bloom_level%5B0%5D=all&parallel%5B0%5D=all&view=image'
    card_request = base.format(id = id)
    r = requests.get(card_request)
    # print('requesting: ' + card_request)
    # print('')
    content = r.content.decode('utf-8', 'ignore')
    content_oneline = ''
    for line in content:
        content_oneline += line.strip()

    cardnumberrx = ">カードナンバー：<span>(.*?)<"
    m = re.search(cardnumberrx, content_oneline)
    card_number = m.group(1)
    # print("card number:")
    # print(card_number)
    card = {}
    card["id"] = card_number

    imgrx = ".*(wp-content/images/cardlist/.*\\.png)"
    m = re.search(imgrx, content)
    # print("img url:")
    image_url = f"https://hololive-official-cardgame.com/{m.group(1)}"
    # print(image_url)
    card["image_url"] = image_url

    namerx = "<h1 class=\"name\">(.*?)</h1>"
    m = re.search(namerx, content)
    card["name"] = m.group(1)


    typerx = "<dt>カードタイプ</dt><dd>(.*?)</dd>"
    m = re.search(typerx, content_oneline)
    card_type = m.group(1)
    # print("card type:")
    # print(card_type)
    card["type"] = card_type

    rarityrx = "<dt>レアリティ</dt><dd>(.*?)</dd>"
    m = re.search(rarityrx, content_oneline)
    card_rarity = m.group(1)
    # print("card rarity:")
    # print(card_rarity)
    card["rarity"] = card_rarity

    tagsrx = "cardlist/cardsearch\\?.*?>(.*?)<"
    card_tags = []
    mz = re.finditer(tagsrx, content_oneline)
    for m in mz:
        card_tags.append(m.group(1))
    # print("card tags")
    # print(card_tags)
    card["tags"] = card_tags

    releaserx = "<dt>収録商品</dt><dd>(.*?)<"
    m = re.search(releaserx, content_oneline)
    card_released = m.group(1)
    # print("released in")
    # print(card_released)
    card["released"] = card_released

    illustratorrx = ">イラストレーター名：<span>(.*?)<"
    m = re.search(illustratorrx, content_oneline)
    if(m):
        card_illustrator = m.group(1)
        # print("illustator:")
        # print(card_illustrator)
        card["illustrator"] =  card_illustrator

    if "ホロメン" in card_type:
        card_colorrx = "色</dt>.*?alt=\"(.*?)\""
        m = re.search(card_colorrx, content_oneline)
        card_color = m.group(1)
        # print("color:")
        # print(card_color)
        card["color"] = card_color
        if "推し" not in card_type:
            # must be non-oshi holomem, get holomem specific fields
            hprx = "<dt>HP</dt><dd>(.*?)<"
            m = re.search(hprx, content_oneline)
            card_hp = m.group(1)
            # print("card hp:")
            # print(card_hp)
            card["hp"] = card_hp

            card_bloomrx = "<dt>Bloomレベル</dt><dd>(.*?)<"
            m = re.search(card_bloomrx, content_oneline)
            card_bloom = m.group(1)
            # print("card bloom:")
            # print(card_bloom)
            card["bloom_level"] = card_bloom

            card_batonrx = "<dt>バトンタッチ</dt>.*?alt=\"(.*?)\""
            m = re.search(card_batonrx, content_oneline)
            card_baton = m.group(1)
            # print("card baton:")
            # print(card_baton)
            card["baton_cost"] = card_baton

            # am beginning to question my decision to use regex to parse these
            # parse arts

            artsrx = "<divclass=\"sparts(.*?)</p></div>"
            mz = re.findall(artsrx, content_oneline)
            arts = []
            arts_index = 0
            for m in mz:
                arts_object = {}
                arts_cost = ''
                arts_costrx = "alt=\"(.)\""
                cost_m = re.finditer(arts_costrx, m)
                for cm in cost_m:
                    arts_cost+=cm.group(1)
                arts_object["cost"] = arts_cost
                arts_tokkourx = "<spanclass=\"tokkou\">.*?alt=\"(.*)\""
                tokkou_m = re.search(arts_tokkourx, m)
                if (tokkou_m):
                    arts_tokkou = tokkou_m.group(1)
                    arts_object["tokkou"] = arts_tokkou
                arts_extra_textrx = "<spanclass=\"tokkou\">.*?</span></span>(.*)"
                extra_m = re.search(arts_extra_textrx, m)
                if(extra_m):
                    arts_extra_text = extra_m.group(1)
                    arts_object["text"] = arts_extra_text
                arts.append(arts_object)

            arts_namerx = "\" />(.*?)<span class=\"tokkou"
            name_m = re.findall(arts_namerx, content)
            for m in name_m:
                tokens = m.split("/>")
                arts_name_and_damage = tokens[-1].split("\u3000")
                arts_name = arts_name_and_damage[0]
                arts_damage = arts_name_and_damage[1]
                arts[arts_index]["name"] = arts_name
                arts[arts_index]["damage"] = arts_damage
                arts_index += 1

            # print(arts)
            card["arts"] = arts

            # still need to figure out how to parse gift, collab and bloom effects
        else:
            # must be an oshi holomen, get oshi holomen specific fields
            pass

    # f = open('output.html', 'w', encoding='utf-8')
    # f.write(content)
    # f.close()

    return card

for i in range(1, 20):
    print(f"parsing {i}")
    card = get_card_from_official_site(i)
    cards[card["id"]] = card

# Convert the list of dictionaries to a JSON string
json_data = json.dumps(cards, indent=4, ensure_ascii=False)

# Optionally, save the JSON string to a file
with open("data.json", "w") as f:
    f.write(json_data)


# with open('soraAzStarter.tsv', 'r') as file:
#     for line in file:
#         values = line.split('\t')
# https://docs.google.com/spreadsheets/d/1IdaueY-Jw8JXjYLOhA9hUd2w0VRBao9Z1URJwmCWJ64/export?gid=474823915&exportFormat=tsv

base_sheet = 'https://docs.google.com/spreadsheets/d/1IdaueY-Jw8JXjYLOhA9hUd2w0VRBao9Z1URJwmCWJ64/export?gid={gid}&exportFormat=tsv'
sheet_gids = []

# gid = 1874575099
# sheet_request = base_sheet.format(gid = gid)
# r = requests.get(sheet_request)
# sheet_content = r.content.decode('utf-8', 'ignore')

# f = open(f'{gid}.tsv', 'w', encoding='utf-8')
# f.write(sheet_content)
# f.close()