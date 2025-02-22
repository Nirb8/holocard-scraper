from io import BytesIO
from PIL import Image
import requests
import re
import json
import cutlet

def get_total_card_number():
    r = requests.get("https://hololive-official-cardgame.com/cardlist/cardsearch/?keyword=&attribute%5B%5D=all&expansion_name=&card_kind%5B%5D=all&rare%5B%5D=all&bloom_level%5B%5D=all&parallel%5B%5D=all")
    # print('requesting for card count ')
    # print('')
    content = r.content.decode('utf-8', 'ignore')

    card_count_rx = "検索結果.*>(\\d+)<.*件"
    m = re.search(card_count_rx, content)

    return int(m.group(1))
def strip_whitespace_brackets_and_quotes_and_lowercase(str):
    return re.sub(r'(\]|\[|:|\\|,|{|}|\"|\s|\u180B|\u200B|\u200C|\u200D|\u2060|\uFEFF)+', '', str).lower()



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

    abilitytextrx = "<dt>能力テキスト</dt><dd>(.*?)</dd>"
    m = re.search(abilitytextrx, content_oneline)
    if(m):
        ability_text_raw = m.group(1)
        ability_text = re.sub('<br/>', '\n', ability_text_raw)
        card["ability_text"] = ability_text

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

            card_bloom_effect_rx = "alt=\"ブルームエフェクト\".*?>\"(.*?)\"</span>\"(.*?)\""
            bloom_m = re.search(card_bloom_effect_rx, content_oneline)
            if (bloom_m):
                bloom_name = m.group(1)
                bloom_text = m.group(2)
                bloom_object = {}
                bloom_object["bloom_name"] = bloom_name
                bloom_object["bloom_text"] = bloom_text
                card["bloom_effect"] = bloom_object
            
            card_collab_effect_rx = "alt=\"コラボエフェクト\".*?>\"(.*?)\"</span>\"(.*?)\""
            collab_m = re.search(card_collab_effect_rx, content_oneline)
            if (collab_m):
                collab_name = m.group(1)
                collab_text = m.group(2)
                collab_object = {}
                collab_object["collab_name"] = collab_name
                collab_object["collab_text"] = collab_text
                card["collab_effect"] = collab_object

            card_gift_effect_rx = "alt=\"ギフト\".*?>\"(.*?)\"</span>\"(.*?)\""
            gift_m = re.search(card_gift_effect_rx, content_oneline)
            if (gift_m):
                gift_name = m.group(1)
                gift_text = m.group(2)
                gift_object = {}
                gift_object["gift_name"] = gift_name
                gift_object["gift_text"] = gift_text
                card["gift_effect"] = gift_object
            return card
            # still need to figure out how to parse gift, collab and bloom effects
        else:
            life_rx = "<dt>LIFE</dt><dd>(.*?)</dd>"
            m = re.search(life_rx, content_oneline)
            card["life"] = int(m.group(1))
            # must be an oshi holomen, get oshi holomen specific fields
            oshi_skill_rx = "<p>推しスキル</p><p>.*?(\\[.*?\\])<span>(.*?)</span>(.*?)</p>"
            m = re.search(oshi_skill_rx, content_oneline)
            oshi_skill = {}
            oshi_skill["name"] = m.group(2)
            oshi_skill["cost_string"] = m.group(1)
            oshi_skill["cost"] = re.search("(\\w+)", m.group(1)).group(1)
            oshi_skill["effect"] = m.group(3)
            card["oshi_skill"] = oshi_skill

            sp_oshi_skill_rx = "<p>SP推しスキル</p><p>.*?(\\[.*?\\])<span>(.*?)</span>(.*?)</p>"
            m = re.search(sp_oshi_skill_rx, content_oneline)
            sp_oshi_skill = {}
            sp_oshi_skill["name"] = m.group(2)
            sp_oshi_skill["cost_string"] = m.group(1)
            sp_oshi_skill["cost"] = int(re.search("(\\d+)", m.group(1)).group(1))
            sp_oshi_skill["effect"] = m.group(3)
            card["sp_oshi_skill"] = sp_oshi_skill
            return card

    # f = open('output.html', 'w', encoding='utf-8')
    # f.write(content)
    # f.close()
    # for "other" cards (support/cheer)

    return card

for i in range(1, 65):
    print(f"parsing {i}")
    card = get_card_from_official_site(i)
    cards[card["id"].lower()] = card




# with open('soraAzStarter.tsv', 'r') as file:
#     for line in file:
#         values = line.split('\t')
# https://docs.google.com/spreadsheets/d/1IdaueY-Jw8JXjYLOhA9hUd2w0VRBao9Z1URJwmCWJ64/export?gid=474823915&exportFormat=tsv

base_sheet = 'https://docs.google.com/spreadsheets/d/1IdaueY-Jw8JXjYLOhA9hUd2w0VRBao9Z1URJwmCWJ64/export?gid={gid}&exportFormat=tsv'
# sheet_gids = [474823915, # SorAz start deck
#               1874575099, # Ayame start deck
#               1673708877, # Okayu start deck
#               1905076073, # Choco start deck
#               994570439, # Blooming Radiance booster
#               1642260809 # Quintet Spectrum booster
#               1114537117, # Starter Cheer set
#               630131808, # PR cards/Birthday Goods
#               1568103987, # Promo Cards
#               ]
sheet_gids = [474823915]

for gid in sheet_gids:
    sheet_request = base_sheet.format(gid = gid)
    r = requests.get(sheet_request)
    sheet_content = r.content.decode('utf-8', 'ignore')
    # print(sheet_content)
    title_row = sheet_content.splitlines()[0].split("\t")
    title_dict = {}
    title_index = 0
    for title in title_row:
        title_dict[title.lower()] = title_index
        title_index += 1
    # Sprint(title_dict)
    sheetlines = sheet_content.splitlines()[1:]
    for line in sheetlines:
        tl_card = line.split("\t")
        # print(tl_card)
        en_content = {}
        card_id = tl_card[0].lower()
        en_content["name"] = tl_card[title_dict["card name \"jp (en)\"".lower()]]
        en_content["type"] = tl_card[title_dict["type"]]
        en_content["color"] = tl_card[title_dict["color"]]
        en_content["tags"] = tl_card[title_dict["tags"]].split(" ")
        en_content["text"] = tl_card[title_dict["text"]]

        if(card_id in cards):
            cards[card_id]["translated_content_en"] = en_content
        
    print(len(sheetlines))

search_strings = {}

for card in cards.values():
    # perform the search string smush/romanization
    card_id = card["id"].lower()
    card_as_json = json.dumps(card, indent=4, ensure_ascii=False)
    card_stripped = strip_whitespace_brackets_and_quotes_and_lowercase(card_as_json)

    katsu = cutlet.Cutlet() # hepburn
    katu = cutlet.Cutlet('kunrei') # kunreishiki
    nkatu = cutlet.Cutlet('nihon') # nihonshiki

    card_stripped_hepburn = strip_whitespace_brackets_and_quotes_and_lowercase(katsu.romaji(card_stripped))
    card_stripped_kunrei = strip_whitespace_brackets_and_quotes_and_lowercase(katu.romaji(card_stripped))
    card_stripped_nihon = strip_whitespace_brackets_and_quotes_and_lowercase(nkatu.romaji(card_stripped))

    total_search_string = f"{card_stripped}|{card_stripped_hepburn}|{card_stripped_kunrei}|{card_stripped_nihon}"
    search_strings[card_id] = total_search_string

for id in search_strings.keys():
    cards[id]["search_string"] = search_strings[id]

# Convert the list of dictionaries to a JSON string
json_data = json.dumps(cards, indent=4, ensure_ascii=False)

# Save the JSON string to a file
with open("data.json", "w") as f:
    f.write(json_data)