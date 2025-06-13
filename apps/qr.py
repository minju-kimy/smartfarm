import qrcode

url = "http://14.32.231.191:8080/"
img = qrcode.make(url)
img.save("smartfarm_ui_qr.png")  # 저장 파일 이름