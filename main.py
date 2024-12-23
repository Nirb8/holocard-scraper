from io import BytesIO
from PIL import Image
import requests
import re
import json


def get_total_card_number():
    r = requests.get("https://hololive-official-cardgame.com/cardlist/cardsearch/?keyword=&attribute%5B%5D=all&expansion_name=&card_kind%5B%5D=all&rare%5B%5D=all&bloom_level%5B%5D=all&parallel%5B%5D=all")
    print('requesting for card count ')
    print('')
    content = r.content.decode('utf-8', 'ignore')

    card_count_rx = "検索結果.*>(\\d+)<.*件"
    m = re.search(card_count_rx, content)

    return int(m.group(1))


cards = {}

# total_cards = get_total_card_number()
# print(f"found {total_cards} total cards")

base = 'https://hololive-official-cardgame.com/cardlist/?id={id}&keyword=&attribute%5B0%5D=all&expansion_name=&card_kind%5B0%5D=all&rare%5B0%5D=all&bloom_level%5B0%5D=all&parallel%5B0%5D=all&view=image'
card_request = base.format(id = 6)
r = requests.get(card_request)
print('requesting: ' + card_request)
print('')
content = r.content.decode('utf-8', 'ignore')
# print(content)
content_oneline = ''
for line in content:
    content_oneline += line.strip()

cardnumberrx = ">カードナンバー：<span>(.*?)<"
m = re.search(cardnumberrx, content_oneline)
card_number = m.group(1)
print("card number:")
print(card_number)

imgrx = ".*(wp-content/images/cardlist/.*\\.png)"
m = re.search(imgrx, content)
print("img url:")
image_url = f"https://hololive-official-cardgame.com/{m.group(1)}"
print(image_url)

typerx = "<dt>カードタイプ</dt><dd>(.*?)</dd>"
m = re.search(typerx, content_oneline)
card_type = m.group(1)
print("card type:")
print(card_type)

rarityrx = "<dt>レアリティ</dt><dd>(.*?)</dd>"
m = re.search(rarityrx, content_oneline)
card_rarity = m.group(1)
print("card rarity:")
print(card_rarity)

tagsrx = "cardlist/cardsearch\\?.*?>(.*?)<"
card_tags = []
mz = re.finditer(tagsrx, content_oneline)
for m in mz:
    card_tags.append(m.group(1))
print("card tags")
print(card_tags)

releaserx = "<dt>収録商品</dt><dd>(.*?)<"
m = re.search(releaserx, content_oneline)
card_released = m.group(1)
print("released in")
print(card_released)

illustratorrx = ">イラストレーター名：<span>(.*?)<"
m = re.search(illustratorrx, content_oneline)
card_illustrator = m.group(1)
print("illustator:")
print(card_illustrator)

if "ホロメン" in card_type:
    card_colorrx = "色</dt>.*?alt=\"(.*?)\""
    m = re.search(card_colorrx, content_oneline)
    card_color = m.group(1)
    print("color:")
    print(card_color)
    if "推し" not in card_type:
        # must be non-oshi holomem, get holomem specific fields
        hprx = "<dt>HP</dt><dd>(.*?)<"
        m = re.search(hprx, content_oneline)
        card_hp = m.group(1)
        print("card hp:")
        print(card_hp)

        card_bloomrx = "<dt>Bloomレベル</dt><dd>(.*?)<"
        m = re.search(card_bloomrx, content_oneline)
        card_bloom = m.group(1)
        print("card bloom:")
        print(card_bloom)

        card_batonrx = "<dt>バトンタッチ</dt>.*?alt=\"(.*?)\""
        m = re.search(card_batonrx, content_oneline)
        card_baton = m.group(1)
        print("card baton:")
        print(card_baton)

        # am beginning to question my decision to use regex to parse these
        # parse arts

        artsrx = "<divclass=\"sparts(.*?)</p></div>"
        arts_strings = []
        mz = re.findall(artsrx, content_oneline)
        print("finding arts")
        for m in mz:
            print(m)
        
        
    else:
        # must be an oshi holomen, get oshi holomen specific fields
        pass




f = open('output.html', 'w', encoding='utf-8')
f.write(content)
f.close()


# with open('soraAzStarter.tsv', 'r') as file:
#     for line in file:
#         values = line.split('\t')
#         print(values)
# https://docs.google.com/spreadsheets/d/1IdaueY-Jw8JXjYLOhA9hUd2w0VRBao9Z1URJwmCWJ64/export?gid=474823915&exportFormat=tsv

base_sheet = 'https://docs.google.com/spreadsheets/d/1IdaueY-Jw8JXjYLOhA9hUd2w0VRBao9Z1URJwmCWJ64/export?gid={gid}&exportFormat=tsv'
sheet_list = []

# gid = 1874575099
# sheet_request = base_sheet.format(gid = gid)
# r = requests.get(sheet_request)
# print('requesting: ' + sheet_request)
# print('')
# sheet_content = r.content.decode('utf-8', 'ignore')

# f = open(f'{gid}.tsv', 'w', encoding='utf-8')
# f.write(sheet_content)
# f.close()