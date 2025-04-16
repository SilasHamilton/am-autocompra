
from flask import Flask, request, jsonify, send_from_directory
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import os

app = Flask(__name__, static_folder='static')

def iniciar_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--log-level=3')
    options.add_argument('--disable-logging')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/executar', methods=['POST'])
def executar():
    data = request.json
    email = data.get('email')
    senha = data.get('senha')
    links = data.get('links', [])

    if not email or not senha or not links:
        return jsonify({'erro': 'Parâmetros incompletos'}), 400

    driver = iniciar_driver()
    driver.get("https://tycoon.airlines-manager.com")
    sleep(2)

    driver.find_element(By.ID, "username").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(senha + Keys.RETURN)
    sleep(5)

    sucesso = 0
    resultados = []

    for link in links:
        try:
            driver.get(link)
            sleep(3)

            try:
                botao_cookie = driver.find_element(By.CLASS_NAME, "cc-dismiss")
                botao_cookie.click()
                sleep(1)
            except:
                pass

            botao = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Confirmar a compra']")
            botao.click()
            sucesso += 1
            resultados.append({'link': link, 'status': 'ok'})
        except Exception as e:
            resultados.append({'link': link, 'status': 'erro', 'detalhes': str(e)})

    driver.quit()

    return jsonify({
        'total': len(links),
        'confirmadas': sucesso,
        'resultados': resultados
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
