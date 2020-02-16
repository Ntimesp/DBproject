import base64
img = open("static/img/battle.jpg", "rb")
img = base64.b64encode(img.read())
print(str(img)[:10])