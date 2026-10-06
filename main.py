import flet as ft
import urllib.request
import json
import threading
from datetime import datetime

class CarCalculatorApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Калькулятор авто 2026"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.padding = 10
        
        # Курсы
        self.rate_usd_krw = 0
        self.rate_usdt_rub = 0
        self.rate_cny_rub = 0
        self.rate_eur_rub = 0
        self.rate_usd_rub = 0
        
        self.create_ui()
        self.load_rates()
    
    def create_ui(self):
        # Верхняя панель курсов
        self.rates_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📊 Актуальные курсы", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.Column([
                            ft.Text("🇰 USD/KRW", size=12, color=ft.Colors.GREY_400),
                            ft.Text("—", size=16, weight=ft.FontWeight.BOLD, key="krw")
                        ], spacing=2),
                        ft.Column([
                            ft.Text("USDT/RUB", size=12, color=ft.Colors.GREY_400),
                            ft.Text("—", size=16, weight=ft.FontWeight.BOLD, key="usdt")
                        ], spacing=2),
                        ft.Column([
                            ft.Text("🇨 CNY/RUB", size=12, color=ft.Colors.GREY_400),
                            ft.Text("—", size=16, weight=ft.FontWeight.BOLD, key="cny")
                        ], spacing=2),
                        ft.Column([
                            ft.Text("EUR/RUB", size=12, color=ft.Colors.GREY_400),
                            ft.Text("—", size=16, weight=ft.FontWeight.BOLD, key="eur")
                        ], spacing=2),
                    ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                    ft.Text("⏳ Загрузка...", size=12, color=ft.Colors.AMBER, key="status")
                ], spacing=10),
                padding=15
            ),
            elevation=5
        )
        
        # Поля ввода
        self.kr_car_cost = ft.TextField(label="💰 Цена авто (KRW)", keyboard_type=ft.KeyboardType.NUMBER, value="22500000")
        self.kr_delivery = ft.TextField(label="🚢 Доставка по Корее", keyboard_type=ft.KeyboardType.NUMBER, value="0")
        self.kr_engine_volume = ft.TextField(label="🔧 Объём двигателя (см³)", keyboard_type=ft.KeyboardType.NUMBER, value="1499", helper_text="Точный из ПТС/VIN")
        self.kr_engine_power = ft.TextField(label="⚡ Мощность (л.с.)", keyboard_type=ft.KeyboardType.NUMBER, value="150", helper_text="Льгота до 160 л.с.", color=ft.Colors.RED_400)
        self.kr_engine_type = ft.Dropdown(label="Тип двигателя", options=[
            ft.dropdown.Option("Бензин"), ft.dropdown.Option("Дизель"),
            ft.dropdown.Option("Электро"), ft.dropdown.Option("Гибрид")
        ], value="Бензин")
        self.kr_age = ft.Dropdown(label="Возраст авто", options=[
            ft.dropdown.Option("до 3 лет"), ft.dropdown.Option("3-5 лет"), ft.dropdown.Option("старше 5 лет")
        ], value="3-5 лет")
        self.kr_personal = ft.Checkbox(label="✅ Для личного пользования (не продавать 12 мес.)", value=True)
        self.kr_broker = ft.TextField(label=" Брокер + СБКТС + ЭПТС (₽)", keyboard_type=ft.KeyboardType.NUMBER, value="110000")
        self.kr_carrier = ft.TextField(label="🚛 Автовоз по РФ (₽)", keyboard_type=ft.KeyboardType.NUMBER, value="200000", helper_text="Зависит от региона", color=ft.Colors.PURPLE_400)
        self.kr_commission = ft.TextField(label="💼 Комиссия (₽)", keyboard_type=ft.KeyboardType.NUMBER, value="50000")
        
        self.cn_car_cost = ft.TextField(label="💰 Цена авто (CNY)", keyboard_type=ft.KeyboardType.NUMBER, value="98000")
        self.cn_docs = ft.TextField(label="📄 Экспорт. документы", keyboard_type=ft.KeyboardType.NUMBER, value="9500")
        self.cn_delivery_border = ft.TextField(label="🚢 Доставка до границы", keyboard_type=ft.KeyboardType.NUMBER, value="4500")
        self.cn_engine_volume = ft.TextField(label="🔧 Объём двигателя (см³)", keyboard_type=ft.KeyboardType.NUMBER, value="1999", helper_text="Точный из ПТС/VIN")
        self.cn_engine_power = ft.TextField(label="⚡ Мощность (л.с.)", keyboard_type=ft.KeyboardType.NUMBER, value="150", helper_text="Льгота до 160 л.с.", color=ft.Colors.RED_400)
        self.cn_engine_type = ft.Dropdown(label="Тип двигателя", options=[
            ft.dropdown.Option("Бензин"), ft.dropdown.Option("Дизель"),
            ft.dropdown.Option("Электро"), ft.dropdown.Option("Гибрид")
        ], value="Бензин")
        self.cn_age = ft.Dropdown(label="Возраст авто", options=[
            ft.dropdown.Option("до 3 лет"), ft.dropdown.Option("3-5 лет"), ft.dropdown.Option("старше 5 лет")
        ], value="3-5 лет")
        self.cn_personal = ft.Checkbox(label="✅ Для личного пользования", value=True)
        self.cn_broker = ft.TextField(label="📋 Брокер + СБКТС + ЭПТС (₽)", keyboard_type=ft.KeyboardType.NUMBER, value="80000")
        self.cn_rereg = ft.TextField(label=" Перегон + регистрация", keyboard_type=ft.KeyboardType.NUMBER, value="15000")
        self.cn_carrier = ft.TextField(label="🚛 Автовоз по РФ (₽)", keyboard_type=ft.KeyboardType.NUMBER, value="200000", helper_text="Зависит от региона", color=ft.Colors.PURPLE_400)
        self.cn_commission = ft.TextField(label="💼 Комиссия (₽)", keyboard_type=ft.KeyboardType.NUMBER, value="50000")
        
        # Результаты
        self.kr_result = ft.Text("Итого Корея: —", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
        self.cn_result = ft.Text("Итого Китай: —", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
        self.kr_details = ft.Text("", size=14, color=ft.Colors.GREY_300)
        self.cn_details = ft.Text("", size=14, color=ft.Colors.GREY_300)
        
        # Вкладки
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="🇰🇷 Корея",
                    content=ft.Column([
                        self.kr_car_cost, self.kr_delivery,
                        ft.Divider(),
                        ft.Text("🔧 Технические данные", size=18, weight=ft.FontWeight.BOLD),
                        self.kr_engine_volume, self.kr_engine_power,
                        self.kr_engine_type, self.kr_age, self.kr_personal,
                        ft.Divider(),
                        ft.Text("🇷🇺 Расходы в РФ", size=18, weight=ft.FontWeight.BOLD),
                        self.kr_broker, self.kr_carrier, self.kr_commission,
                        ft.ElevatedButton(" РАССЧИТАТЬ КОРЕЮ", on_click=self.calc_korea, 
                                         color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_600,
                                         height=50, width=float("inf")),
                        self.kr_result, self.kr_details
                    ], scroll=ft.ScrollMode.AUTO, spacing=10)
                ),
                ft.Tab(
                    text="🇨🇳 Китай",
                    content=ft.Column([
                        self.cn_car_cost, self.cn_docs, self.cn_delivery_border,
                        ft.Divider(),
                        ft.Text("🔧 Технические данные", size=18, weight=ft.FontWeight.BOLD),
                        self.cn_engine_volume, self.cn_engine_power,
                        self.cn_engine_type, self.cn_age, self.cn_personal,
                        ft.Divider(),
                        ft.Text("🇷🇺 Расходы в РФ", size=18, weight=ft.FontWeight.BOLD),
                        self.cn_broker, self.cn_rereg, self.cn_carrier, self.cn_commission,
                        ft.ElevatedButton("🧮 РАССЧИТАТЬ КИТАЙ", on_click=self.calc_china,
                                         color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_600,
                                         height=50, width=float("inf")),
                        self.cn_result, self.cn_details
                    ], scroll=ft.ScrollMode.AUTO, spacing=10)
                ),
            ],
            expand=1
        )
        
        self.page.add(
            self.rates_card,
            ft.SizedBox(height=10),
            self.tabs
        )
    
    def load_rates(self):
        def fetch():
            try:
                req = urllib.request.Request("https://www.cbr-xml-daily.ru/daily_json.js", headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as r:
                    data = json.loads(r.read().decode('utf-8'))
                self.rate_usd_rub = data['Valute']['USD']['Value']
                self.rate_eur_rub = data['Valute']['EUR']['Value']
                self.rate_cny_rub = data['Valute']['CNY']['Value']
                
                req2 = urllib.request.Request("https://open.er-api.com/v6/latest/USD", headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req2, timeout=10) as r:
                    data2 = json.loads(r.read().decode('utf-8'))
                self.rate_usd_krw = data2['rates']['KRW']
                
                req3 = urllib.request.Request("https://api.binance.com/api/v3/ticker/price?symbol=USDTRUB", headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req3, timeout=10) as r:
                    self.rate_usdt_rub = float(json.loads(r.read().decode('utf-8'))['price'])
                
                self.page.run_task(self.update_rates_ui)
            except Exception as e:
                self.page.run_task(lambda: self.update_status(f"⚠ Ошибка: {str(e)[:30]}"))
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def update_rates_ui(self):
        for ctrl in self.rates_card.content.content.controls[1].controls:
            if ctrl.controls[1].key == "krw":
                ctrl.controls[1].value = f"{self.rate_usd_krw:.2f} ₩"
            elif ctrl.controls[1].key == "usdt":
                ctrl.controls[1].value = f"{self.rate_usdt_rub:.2f} ₽"
            elif ctrl.controls[1].key == "cny":
                ctrl.controls[1].value = f"{self.rate_cny_rub:.2f} ₽"
            elif ctrl.controls[1].key == "eur":
                ctrl.controls[1].value = f"{self.rate_eur_rub:.2f} ₽"
        self.update_status(f"✅ Обновлено: {datetime.now().strftime('%H:%M')}")
        self.page.update()
    
    def update_status(self, text):
        self.rates_card.content.content.controls[2].value = text
    
    def get_customs_fee(self, cost):
        if cost <= 200000: return 775
        elif cost <= 450000: return 1550
        elif cost <= 1200000: return 3100
        elif cost <= 2000000: return 8530
        elif cost <= 4500000: return 12000
        elif cost <= 10000000: return 20000
        else: return 30000
    
    def calc_util(self, vol, power, age, personal, etype):
        eligible = False
        if personal:
            if etype in ["Электро", "Гибрид"]:
                if power <= 80: eligible = True
            else:
                if vol <= 3000 and power <= 160: eligible = True
        if eligible:
            return 3400 if age == "до 3 лет" else 5200
        if vol <= 1000: return 306100
        elif vol <= 2000:
            if power <= 160: return 800800
            elif power <= 190: return 900000
            else: return 2250400
        elif vol <= 3000:
            return 2250400 if power <= 160 else 3500000
        else: return 3500000
    
    def calc_duty(self, cost_rub, vol, age, eur):
        cost_eur = cost_rub / eur if eur > 0 else 0
        if age == "до 3 лет":
            pct = 0.48 if cost_eur <= 8500 else 0.54
            by_pct = cost_eur * pct
            min_e = 1.5 if vol<=1000 else 1.7 if vol<=1500 else 2.5 if vol<=1800 else 2.7 if vol<=2300 else 3.0 if vol<=3000 else 3.6
            return max(by_pct, vol * min_e) * eur
        elif age == "3-5 лет":
            r = 1.5 if vol<=1000 else 1.7 if vol<=1500 else 2.5 if vol<=1800 else 2.7 if vol<=2300 else 3.0 if vol<=3000 else 3.6
            return vol * r * eur
        else:
            r = 3.0 if vol<=1000 else 3.2 if vol<=1500 else 3.5 if vol<=1800 else 4.8 if vol<=2300 else 5.0 if vol<=3000 else 5.7
            return vol * r * eur
    
    def calc_korea(self, e):
        try:
            total_krw = float(self.kr_car_cost.value) + float(self.kr_delivery.value)
            base_usdt = total_krw / self.rate_usd_krw
            base_rub = base_usdt * self.rate_usdt_rub
            
            duty = self.calc_duty(base_rub, float(self.kr_engine_volume.value), self.kr_age.value, self.rate_eur_rub)
            fee = self.get_customs_fee(base_rub)
            util = self.calc_util(float(self.kr_engine_volume.value), float(self.kr_engine_power.value), 
                                  self.kr_age.value, self.kr_personal.value, self.kr_engine_type.value)
            
            total = base_rub + duty + fee + util + float(self.kr_broker.value) + float(self.kr_carrier.value) + float(self.kr_commission.value)
            
            self.kr_result.value = f"🇰🇷 Итого: {total:,.0f} ₽"
            self.kr_details.value = f"Авто: {base_rub:,.0f} | Пошлина: {duty:,.0f} | Сбор: {fee:,.0f} | Утиль: {util:,.0f}"
            self.page.update()
        except Exception as ex:
            self.kr_result.value = f"Ошибка: {ex}"
            self.page.update()
    
    def calc_china(self, e):
        try:
            total_cny = float(self.cn_car_cost.value) + float(self.cn_docs.value) + float(self.cn_delivery_border.value)
            base_rub = total_cny * self.rate_cny_rub
            
            duty = self.calc_duty(base_rub, float(self.cn_engine_volume.value), self.cn_age.value, self.rate_eur_rub)
            fee = self.get_customs_fee(base_rub)
            util = self.calc_util(float(self.cn_engine_volume.value), float(self.cn_engine_power.value),
                                  self.cn_age.value, self.cn_personal.value, self.cn_engine_type.value)
            
            total = base_rub + duty + fee + util + float(self.cn_broker.value) + float(self.cn_rereg.value) + float(self.cn_carrier.value) + float(self.cn_commission.value)
            
            self.cn_result.value = f"🇨 Итого: {total:,.0f} ₽"
            self.cn_details.value = f"Авто: {base_rub:,.0f} | Пошлина: {duty:,.0f} | Сбор: {fee:,.0f} | Утиль: {util:,.0f}"
            self.page.update()
        except Exception as ex:
            self.cn_result.value = f"Ошибка: {ex}"
            self.page.update()

def main(page: ft.Page):
    CarCalculatorApp(page)

ft.app(target=main)