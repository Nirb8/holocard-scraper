from io import BytesIO
from PIL import Image
import requests
import re

base = 'https://hololive-official-cardgame.com/cardlist/?id={id}&keyword=&attribute%5B0%5D=all&expansion_name=&card_kind%5B0%5D=all&rare%5B0%5D=all&bloom_level%5B0%5D=all&parallel%5B0%5D=all&view=image'
card_request = base.format(id = 1)
r = requests.get(card_request)
print('requesting: ' + card_request)
print('')
content = r.content.decode('utf-8', 'ignore')
print(content)

imgrx = ".*(wp-content/images/cardlist/.*\.png)"
m = re.search(imgrx, content)
print(m.group(1))

# f = open('output.html', 'w', encoding='utf-8')
# f.write(content)
# f.close()



response = requests.get("https://hololive-official-cardgame.com/wp-content/images/cardlist/hSD01/hSD01-001_OSR.png")
img = Image.open(BytesIO(response.content))
img.save("imgs/image.png")
