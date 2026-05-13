"""
Dokon Boshqaruv Dasturi
Nasiya va to'lovlarni kuzatish uchun
"""

import json
import os
from datetime import datetime

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.widget import Widget

# ===================== MA'LUMOTLAR BAZASI =====================

DATA_FILE = "dokon_data.json"

def ma_lumot_yuklash():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "mijozlar": [],
        "hamkorlar": [],
        "tranzaksiyalar": [],
        "sozlamalar": {
            "dokon_nomi": "Mening Do'konim",
            "egasi": "Do'kon Egasi"
        }
    }

def ma_lumot_saqlash(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Global ma'lumotlar
app_data = ma_lumot_yuklash()

# ===================== RANGLAR VA STIL =====================

RANGLAR = {
    "asosiy": (0.13, 0.59, 0.95, 1),
    "yashil": (0.18, 0.8, 0.44, 1),
    "qizil": (0.91, 0.3, 0.24, 1),
    "to'q": (0.1, 0.1, 0.15, 1),
    "fon": (0.96, 0.97, 0.99, 1),
    "oq": (1, 1, 1, 1),
    "kulrang": (0.6, 0.6, 0.65, 1),
    "sarlavha": (0.08, 0.08, 0.12, 1),
}

def raqam_formati(summa):
    return f"{summa:,.0f} so'm".replace(",", " ")

# ===================== MAXSUS WIDGET'LAR =====================

class RangliTugma(Button):
    def __init__(self, rang=(0.13, 0.59, 0.95, 1), matn_rangi=(1,1,1,1), **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_color = rang
        self.color = matn_rangi
        self.font_size = dp(14)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(48)

class Karta(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self._yangilash, size=self._yangilash)
        self.padding = [dp(16), dp(12)]

    def _yangilash(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

# ===================== NASIYA QO'SHISH POPUP =====================

class NasiyaQoshishPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = "Nasiya Qo'shish"
        self.size_hint = (0.95, 0.92)
        self.background = ""
        self.background_color = (0, 0, 0, 0.6)

        asosiy = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(16))

        # Sarlavha
        sarlavha = Label(
            text="📝 Yangi Nasiya",
            font_size=dp(18),
            bold=True,
            color=RANGLAR["sarlavha"],
            size_hint_y=None,
            height=dp(40)
        )
        asosiy.add_widget(sarlavha)

        # Mijoz ismi
        asosiy.add_widget(Label(text="Mijoz ismi *", color=RANGLAR["kulrang"],
                                size_hint_y=None, height=dp(24), halign="left",
                                text_size=(None, None)))
        self.ism_input = TextInput(
            hint_text="Ism Familiya",
            multiline=False,
            size_hint_y=None,
            height=dp(44),
            font_size=dp(14),
            padding=[dp(12), dp(10)]
        )
        asosiy.add_widget(self.ism_input)

        # Summa
        asosiy.add_widget(Label(text="Nasiya summasi (so'm) *", color=RANGLAR["kulrang"],
                                size_hint_y=None, height=dp(24)))
        self.summa_input = TextInput(
            hint_text="Masalan: 150000",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(44),
            font_size=dp(14),
            padding=[dp(12), dp(10)]
        )
        asosiy.add_widget(self.summa_input)

        # Mahsulotlar
        asosiy.add_widget(Label(text="Olingan mahsulotlar", color=RANGLAR["kulrang"],
                                size_hint_y=None, height=dp(24)))
        self.mahsulot_input = TextInput(
            hint_text="Masalan: Non x2, Yog' 1L, Shakar 2kg...",
            multiline=True,
            size_hint_y=None,
            height=dp(80),
            font_size=dp(14),
            padding=[dp(12), dp(10)]
        )
        asosiy.add_widget(self.mahsulot_input)

        # Izoh
        asosiy.add_widget(Label(text="Izoh (ixtiyoriy)", color=RANGLAR["kulrang"],
                                size_hint_y=None, height=dp(24)))
        self.izoh_input = TextInput(
            hint_text="Qo'shimcha ma'lumot...",
            multiline=False,
            size_hint_y=None,
            height=dp(44),
            font_size=dp(14),
            padding=[dp(12), dp(10)]
        )
        asosiy.add_widget(self.izoh_input)

        # Sana
        hozir = datetime.now()
        sana_matn = hozir.strftime("%Y-%m-%d %H:%M")
        asosiy.add_widget(Label(
            text=f"🕐 Sana: {sana_matn}",
            color=RANGLAR["kulrang"],
            font_size=dp(12),
            size_hint_y=None,
            height=dp(28)
        ))

        # Tugmalar
        tugmalar = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))
        bekor = RangliTugma(rang=(0.85, 0.85, 0.9, 1), matn_rangi=(0.3, 0.3, 0.35, 1),
                            text="Bekor qilish")
        bekor.bind(on_press=lambda x: self.dismiss())
        saqlash = RangliTugma(rang=RANGLAR["yashil"], text="✅ Saqlash")
        saqlash.bind(on_press=self.saqlash)
        tugmalar.add_widget(bekor)
        tugmalar.add_widget(saqlash)
        asosiy.add_widget(tugmalar)

        self.content = asosiy

    def saqlash(self, *args):
        ism = self.ism_input.text.strip()
        summa_txt = self.summa_input.text.strip()

        if not ism or not summa_txt:
            xato_popup = Popup(
                title="Xatolik",
                content=Label(text="Ism va summa kiritilishi shart!"),
                size_hint=(0.7, 0.3)
            )
            xato_popup.open()
            return

        summa = float(summa_txt)
        hozir = datetime.now()

        tranzaksiya = {
            "id": len(app_data["tranzaksiyalar"]) + 1,
            "tur": "nasiya",
            "mijoz": ism,
            "summa": summa,
            "mahsulotlar": self.mahsulot_input.text.strip(),
            "izoh": self.izoh_input.text.strip(),
            "sana": hozir.strftime("%Y-%m-%d"),
            "vaqt": hozir.strftime("%H:%M"),
            "holat": "ochiq"
        }

        app_data["tranzaksiyalar"].insert(0, tranzaksiya)

        # Mijozlar ro'yxatiga qo'shish
        mavjud = False
        for m in app_data["mijozlar"]:
            if m["ism"].lower() == ism.lower():
                m["jami_nasiya"] = m.get("jami_nasiya", 0) + summa
                mavjud = True
                break
        if not mavjud:
            app_data["mijozlar"].append({
                "ism": ism,
                "jami_nasiya": summa,
                "jami_tolangan": 0
            })

        ma_lumot_saqlash(app_data)
        self.dismiss()
        if self.callback:
            self.callback()

# ===================== TO'LOV QILISH POPUP =====================

class TolovjQilishPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = "To'lov Qilish"
        self.size_hint = (0.92, 0.7)

        asosiy = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(16))

        asosiy.add_widget(Label(text="💳 To'lov Qilish", font_size=dp(18), bold=True,
                                color=RANGLAR["sarlavha"], size_hint_y=None, height=dp(40)))

        asosiy.add_widget(Label(text="Mijoz ismi *", color=RANGLAR["kulrang"],
                                size_hint_y=None, height=dp(24)))
        self.ism_input = TextInput(hint_text="Ism Familiya", multiline=False,
                                   size_hint_y=None, height=dp(44),
                                   font_size=dp(14), padding=[dp(12), dp(10)])
        asosiy.add_widget(self.ism_input)

        asosiy.add_widget(Label(text="To'lov summasi (so'm) *", color=RANGLAR["kulrang"],
                                size_hint_y=None, height=dp(24)))
        self.summa_input = TextInput(hint_text="Masalan: 50000", multiline=False,
                                     input_filter="float", size_hint_y=None,
                                     height=dp(44), font_size=dp(14),
                                     padding=[dp(12), dp(10)])
        asosiy.add_widget(self.summa_input)

        asosiy.add_widget(Label(text="Izoh", color=RANGLAR["kulrang"],
                                size_hint_y=None, height=dp(24)))
        self.izoh_input = TextInput(hint_text="Qo'shimcha ma'lumot...", multiline=False,
                                    size_hint_y=None, height=dp(44),
                                    font_size=dp(14), padding=[dp(12), dp(10)])
        asosiy.add_widget(self.izoh_input)

        tugmalar = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))
        bekor = RangliTugma(rang=(0.85, 0.85, 0.9, 1), matn_rangi=(0.3,0.3,0.35,1),
                            text="Bekor qilish")
        bekor.bind(on_press=lambda x: self.dismiss())
        saqlash = RangliTugma(rang=RANGLAR["asosiy"], text="💳 To'lovni saqlash")
        saqlash.bind(on_press=self.saqlash)
        tugmalar.add_widget(bekor)
        tugmalar.add_widget(saqlash)
        asosiy.add_widget(tugmalar)

        self.content = asosiy

    def saqlash(self, *args):
        ism = self.ism_input.text.strip()
        summa_txt = self.summa_input.text.strip()

        if not ism or not summa_txt:
            return

        summa = float(summa_txt)
        hozir = datetime.now()

        tranzaksiya = {
            "id": len(app_data["tranzaksiyalar"]) + 1,
            "tur": "tolov",
            "mijoz": ism,
            "summa": summa,
            "mahsulotlar": "",
            "izoh": self.izoh_input.text.strip(),
            "sana": hozir.strftime("%Y-%m-%d"),
            "vaqt": hozir.strftime("%H:%M"),
            "holat": "yopiq"
        }

        app_data["tranzaksiyalar"].insert(0, tranzaksiya)

        for m in app_data["mijozlar"]:
            if m["ism"].lower() == ism.lower():
                m["jami_tolangan"] = m.get("jami_tolangan", 0) + summa
                break

        ma_lumot_saqlash(app_data)
        self.dismiss()
        if self.callback:
            self.callback()

# ===================== BOQ SAHIFA =====================

class BoshSahifa(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._qurish()

    def _qurish(self):
        self.clear_widgets()
        asosiy = BoxLayout(orientation="vertical")

        # Yuqori panel
        yuqori = BoxLayout(size_hint_y=None, height=dp(70), padding=[dp(16), dp(12)])
        with yuqori.canvas.before:
            Color(*RANGLAR["asosiy"])
            self.yuqori_bg = Rectangle(pos=yuqori.pos, size=yuqori.size)
        yuqori.bind(pos=lambda w, v: setattr(self.yuqori_bg, 'pos', v),
                    size=lambda w, v: setattr(self.yuqori_bg, 'size', v))

        sozlamalar = app_data.get("sozlamalar", {})
        sarlavha = Label(
            text=f"🏪 {sozlamalar.get('dokon_nomi', 'Mening Dokonim')}",
            font_size=dp(20),
            bold=True,
            color=RANGLAR["oq"]
        )
        yuqori.add_widget(sarlavha)
        asosiy.add_widget(yuqori)

        # Kontent
        scroll = ScrollView()
        kontent = BoxLayout(orientation="vertical", spacing=dp(12),
                            padding=[dp(12), dp(12)], size_hint_y=None)
        kontent.bind(minimum_height=kontent.setter("height"))

        # Statistika hisoblash
        jami_nasiya = sum(t["summa"] for t in app_data["tranzaksiyalar"] if t["tur"] == "nasiya")
        jami_tolov = sum(t["summa"] for t in app_data["tranzaksiyalar"] if t["tur"] == "tolov")
        qolgan_qarz = jami_nasiya - jami_tolov

        # Asosiy statistika kartasi
        stat_karta = BoxLayout(orientation="vertical", size_hint_y=None,
                               height=dp(160), padding=dp(16), spacing=dp(8))
        with stat_karta.canvas.before:
            Color(0.1, 0.45, 0.85, 1)
            self.stat_bg = RoundedRectangle(pos=stat_karta.pos, size=stat_karta.size,
                                            radius=[dp(16)])
        stat_karta.bind(pos=lambda w, v: setattr(self.stat_bg, 'pos', v),
                        size=lambda w, v: setattr(self.stat_bg, 'size', v))

        stat_karta.add_widget(Label(text="Jami berilgan nasiya", color=(0.8, 0.9, 1, 1),
                                    font_size=dp(13), size_hint_y=None, height=dp(24)))
        stat_karta.add_widget(Label(text=raqam_formati(jami_nasiya), color=RANGLAR["oq"],
                                    font_size=dp(26), bold=True, size_hint_y=None, height=dp(40)))

        qolgan_qism = BoxLayout(spacing=dp(20), size_hint_y=None, height=dp(60))

        qarz_box = BoxLayout(orientation="vertical")
        qarz_box.add_widget(Label(text="Qolgan qarz", color=(0.8, 0.9, 1, 0.8),
                                  font_size=dp(11)))
        qarz_box.add_widget(Label(text=raqam_formati(qolgan_qarz),
                                  color=(1, 0.9, 0.5, 1), font_size=dp(15), bold=True))

        tolov_box = BoxLayout(orientation="vertical")
        tolov_box.add_widget(Label(text="Jami to'langan", color=(0.8, 0.9, 1, 0.8),
                                   font_size=dp(11)))
        tolov_box.add_widget(Label(text=raqam_formati(jami_tolov),
                                   color=(0.5, 1, 0.7, 1), font_size=dp(15), bold=True))

        qolgan_qism.add_widget(qarz_box)
        qolgan_qism.add_widget(tolov_box)
        stat_karta.add_widget(qolgan_qism)
        kontent.add_widget(stat_karta)

        # Tugmalar
        tugmalar = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(52))
        nasiya_tugma = RangliTugma(rang=RANGLAR["qizil"], text="➕ Nasiya qo'shish")
        nasiya_tugma.bind(on_press=self.nasiya_qoshish)
        tolov_tugma = RangliTugma(rang=RANGLAR["yashil"], text="💳 To'lov qilish")
        tolov_tugma.bind(on_press=self.tolov_qilish)
        tugmalar.add_widget(nasiya_tugma)
        tugmalar.add_widget(tolov_tugma)
        kontent.add_widget(tugmalar)

        # So'nggi tranzaksiyalar
        kontent.add_widget(Label(text="So'nggi faoliyat", font_size=dp(16), bold=True,
                                 color=RANGLAR["sarlavha"], size_hint_y=None, height=dp(36),
                                 halign="left", text_size=(Window.width - dp(24), None)))

        if not app_data["tranzaksiyalar"]:
            kontent.add_widget(Label(text="Hali tranzaksiya yo'q.\nNasiya yoki to'lov qo'shing.",
                                     color=RANGLAR["kulrang"], font_size=dp(14),
                                     size_hint_y=None, height=dp(80), halign="center",
                                     text_size=(Window.width - dp(48), None)))
        else:
            for t in app_data["tranzaksiyalar"][:20]:
                karta = self._tranzaksiya_karta(t)
                kontent.add_widget(karta)

        scroll.add_widget(kontent)
        asosiy.add_widget(scroll)
        self.add_widget(asosiy)

    def _tranzaksiya_karta(self, t):
        karta = BoxLayout(orientation="vertical", size_hint_y=None,
                          padding=[dp(14), dp(10)], spacing=dp(4))
        karta.height = dp(100) if t.get("mahsulotlar") else dp(76)

        with karta.canvas.before:
            Color(1, 1, 1, 1)
            rect = RoundedRectangle(pos=karta.pos, size=karta.size, radius=[dp(10)])
        karta.bind(pos=lambda w, v: setattr(rect, 'pos', v),
                   size=lambda w, v: setattr(rect, 'size', v))

        ustun = BoxLayout()
        rang = RANGLAR["qizil"] if t["tur"] == "nasiya" else RANGLAR["yashil"]
        belgi = "📤" if t["tur"] == "nasiya" else "📥"
        tur_matn = "NASIYA" if t["tur"] == "nasiya" else "TO'LOV"

        chap = BoxLayout(orientation="vertical")
        chap.add_widget(Label(text=f"{belgi} {t['mijoz']}", font_size=dp(15), bold=True,
                              color=RANGLAR["sarlavha"], halign="left",
                              text_size=(Window.width * 0.55, None), size_hint_y=None,
                              height=dp(24)))
        chap.add_widget(Label(text=f"{t['sana']} | {t['vaqt']}", font_size=dp(11),
                              color=RANGLAR["kulrang"], halign="left",
                              text_size=(Window.width * 0.55, None),
                              size_hint_y=None, height=dp(18)))
        if t.get("mahsulotlar"):
            chap.add_widget(Label(text=f"📦 {t['mahsulotlar'][:40]}...",
                                  font_size=dp(11), color=RANGLAR["kulrang"],
                                  halign="left", text_size=(Window.width * 0.55, None),
                                  size_hint_y=None, height=dp(18)))

        ong = BoxLayout(orientation="vertical", size_hint_x=0.4)
        ong.add_widget(Label(text=f"{'+' if t['tur']=='nasiya' else '-'}{raqam_formati(t['summa'])}",
                             font_size=dp(13), bold=True, color=rang,
                             halign="right", text_size=(None, None), size_hint_y=None, height=dp(28)))
        ong.add_widget(Label(text=tur_matn, font_size=dp(10), color=rang,
                             halign="right", text_size=(None, None), size_hint_y=None, height=dp(18)))

        ustun.add_widget(chap)
        ustun.add_widget(ong)
        karta.add_widget(ustun)

        # Chiziq
        separator = Widget(size_hint_y=None, height=dp(1))
        with separator.canvas:
            Color(0.93, 0.93, 0.96, 1)
            Rectangle(pos=separator.pos, size=separator.size)
        return karta

    def nasiya_qoshish(self, *args):
        popup = NasiyaQoshishPopup(callback=self._yangilash)
        popup.open()

    def tolov_qilish(self, *args):
        popup = TolovjQilishPopup(callback=self._yangilash)
        popup.open()

    def _yangilash(self):
        self._qurish()

    def on_enter(self):
        self._qurish()

# ===================== MIJOZLAR SAHIFASI =====================

class MijozlarSahifasi(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._qurish()

    def _qurish(self):
        self.clear_widgets()
        asosiy = BoxLayout(orientation="vertical")

        yuqori = BoxLayout(size_hint_y=None, height=dp(60), padding=[dp(16), dp(10)])
        with yuqori.canvas.before:
            Color(*RANGLAR["asosiy"])
            bg = Rectangle(pos=yuqori.pos, size=yuqori.size)
        yuqori.bind(pos=lambda w, v: setattr(bg, 'pos', v),
                    size=lambda w, v: setattr(bg, 'size', v))
        yuqori.add_widget(Label(text="👥 Mijozlar", font_size=dp(20), bold=True,
                                color=RANGLAR["oq"]))
        asosiy.add_widget(yuqori)

        scroll = ScrollView()
        kontent = BoxLayout(orientation="vertical", spacing=dp(8),
                            padding=[dp(12), dp(12)], size_hint_y=None)
        kontent.bind(minimum_height=kontent.setter("height"))

        if not app_data["mijozlar"]:
            kontent.add_widget(Label(
                text="Hali mijoz yo'q.\nBosh sahifadan nasiya qo'shing.",
                color=RANGLAR["kulrang"], font_size=dp(14),
                size_hint_y=None, height=dp(100), halign="center",
                text_size=(Window.width - dp(48), None)))
        else:
            for m in sorted(app_data["mijozlar"], key=lambda x: x.get("jami_nasiya", 0), reverse=True):
                karta = self._mijoz_karta(m)
                kontent.add_widget(karta)

        scroll.add_widget(kontent)
        asosiy.add_widget(scroll)
        self.add_widget(asosiy)

    def _mijoz_karta(self, m):
        nasiya = m.get("jami_nasiya", 0)
        tolangan = m.get("jami_tolangan", 0)
        qolgan = nasiya - tolangan

        karta = BoxLayout(orientation="vertical", size_hint_y=None,
                          height=dp(110), padding=[dp(14), dp(12)], spacing=dp(6))
        with karta.canvas.before:
            Color(1, 1, 1, 1)
            rect = RoundedRectangle(pos=karta.pos, size=karta.size, radius=[dp(12)])
        karta.bind(pos=lambda w, v: setattr(rect, 'pos', v),
                   size=lambda w, v: setattr(rect, 'size', v))

        sarlavha = BoxLayout(size_hint_y=None, height=dp(30))
        sarlavha.add_widget(Label(text=f"👤 {m['ism']}", font_size=dp(16), bold=True,
                                  color=RANGLAR["sarlavha"], halign="left",
                                  text_size=(Window.width * 0.6, None)))
        rang = RANGLAR["qizil"] if qolgan > 0 else RANGLAR["yashil"]
        sarlavha.add_widget(Label(text=f"Qarz: {raqam_formati(qolgan)}",
                                  font_size=dp(14), bold=True, color=rang,
                                  halign="right", text_size=(None, None)))
        karta.add_widget(sarlavha)

        tafsilot = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        nas_box = BoxLayout(orientation="vertical")
        nas_box.add_widget(Label(text="Jami nasiya", font_size=dp(11),
                                 color=RANGLAR["kulrang"]))
        nas_box.add_widget(Label(text=raqam_formati(nasiya), font_size=dp(13),
                                 bold=True, color=RANGLAR["qizil"]))

        tol_box = BoxLayout(orientation="vertical")
        tol_box.add_widget(Label(text="To'langan", font_size=dp(11),
                                 color=RANGLAR["kulrang"]))
        tol_box.add_widget(Label(text=raqam_formati(tolangan), font_size=dp(13),
                                 bold=True, color=RANGLAR["yashil"]))

        tafsilot.add_widget(nas_box)
        tafsilot.add_widget(tol_box)
        karta.add_widget(tafsilot)

        return karta

    def on_enter(self):
        self._qurish()

# ===================== HAMKORLAR SAHIFASI =====================

class HamkorlarSahifasi(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._qurish()

    def _qurish(self):
        self.clear_widgets()
        asosiy = BoxLayout(orientation="vertical")

        yuqori = BoxLayout(size_hint_y=None, height=dp(60), padding=[dp(16), dp(10)])
        with yuqori.canvas.before:
            Color(*RANGLAR["asosiy"])
            bg = Rectangle(pos=yuqori.pos, size=yuqori.size)
        yuqori.bind(pos=lambda w, v: setattr(bg, 'pos', v),
                    size=lambda w, v: setattr(bg, 'size', v))

        sarlavha_box = BoxLayout()
        sarlavha_box.add_widget(Label(text="🤝 Hamkorlar", font_size=dp(20), bold=True,
                                      color=RANGLAR["oq"]))
        hamkor_qosh = Button(text="+ Qo'shish", size_hint_x=None, width=dp(100),
                             background_color=RANGLAR["yashil"], color=RANGLAR["oq"],
                             bold=True, background_normal="")
        hamkor_qosh.bind(on_press=self.hamkor_qoshish)
        sarlavha_box.add_widget(hamkor_qosh)
        yuqori.add_widget(sarlavha_box)
        asosiy.add_widget(yuqori)

        scroll = ScrollView()
        self.kontent = BoxLayout(orientation="vertical", spacing=dp(8),
                                 padding=[dp(12), dp(12)], size_hint_y=None)
        self.kontent.bind(minimum_height=self.kontent.setter("height"))

        self._hamkorlarni_chiz()

        scroll.add_widget(self.kontent)
        asosiy.add_widget(scroll)
        self.add_widget(asosiy)

    def _hamkorlarni_chiz(self):
        self.kontent.clear_widgets()

        if not app_data["hamkorlar"]:
            self.kontent.add_widget(Label(
                text="Hali hamkor yo'q.\n+ Qo'shish tugmasini bosing.",
                color=RANGLAR["kulrang"], font_size=dp(14),
                size_hint_y=None, height=dp(100), halign="center",
                text_size=(Window.width - dp(48), None)))
        else:
            for h in app_data["hamkorlar"]:
                self.kontent.add_widget(self._hamkor_karta(h))

    def _hamkor_karta(self, h):
        karta = BoxLayout(size_hint_y=None, height=dp(80),
                          padding=[dp(14), dp(12)], spacing=dp(10))
        with karta.canvas.before:
            Color(1, 1, 1, 1)
            rect = RoundedRectangle(pos=karta.pos, size=karta.size, radius=[dp(12)])
        karta.bind(pos=lambda w, v: setattr(rect, 'pos', v),
                   size=lambda w, v: setattr(rect, 'size', v))

        info = BoxLayout(orientation="vertical")
        info.add_widget(Label(text=f"🏢 {h['ism']}", font_size=dp(15), bold=True,
                              color=RANGLAR["sarlavha"], halign="left",
                              text_size=(Window.width * 0.5, None), size_hint_y=None,
                              height=dp(28)))
        info.add_widget(Label(text=f"📞 {h.get('telefon', '-')}",
                              font_size=dp(12), color=RANGLAR["kulrang"],
                              halign="left", text_size=(Window.width * 0.5, None),
                              size_hint_y=None, height=dp(20)))

        qarz_box = BoxLayout(orientation="vertical", size_hint_x=0.4)
        qarz = h.get("qarzdorlik", 0)
        rang = RANGLAR["qizil"] if qarz > 0 else RANGLAR["yashil"]
        qarz_box.add_widget(Label(text="Hisoblaşuv", font_size=dp(11),
                                  color=RANGLAR["kulrang"]))
        qarz_box.add_widget(Label(text=raqam_formati(abs(qarz)),
                                  font_size=dp(14), bold=True, color=rang))

        karta.add_widget(info)
        karta.add_widget(qarz_box)
        return karta

    def hamkor_qoshish(self, *args):
        popup = self._hamkor_popup()
        popup.open()

    def _hamkor_popup(self):
        pop = Popup(title="Hamkor Qo'shish", size_hint=(0.92, 0.65))
        asosiy = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(16))

        asosiy.add_widget(Label(text="Hamkor/Tashkilot nomi *", color=RANGLAR["kulrang"],
                                size_hint_y=None, height=dp(24)))
        ism_inp = TextInput(hint_text="Masalan: Farrux Toshmatov",
                            multiline=False, size_hint_y=None, height=dp(44),
                            font_size=dp(14), padding=[dp(12), dp(10)])
        asosiy.add_widget(ism_inp)

        asosiy.add_widget(Label(text="Telefon raqami", color=RANGLAR["kulrang"],
                                size_hint_y=None, height=dp(24)))
        tel_inp = TextInput(hint_text="+998 XX XXX XX XX", multiline=False,
                            size_hint_y=None, height=dp(44),
                            font_size=dp(14), padding=[dp(12), dp(10)])
        asosiy.add_widget(tel_inp)

        asosiy.add_widget(Label(text="Qarzdorlik summasi (so'm)",
                                color=RANGLAR["kulrang"], size_hint_y=None, height=dp(24)))
        qarz_inp = TextInput(hint_text="0 (manfiy = biz qarzli)",
                             multiline=False, input_filter="float",
                             size_hint_y=None, height=dp(44),
                             font_size=dp(14), padding=[dp(12), dp(10)])
        asosiy.add_widget(qarz_inp)

        tugmalar = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))

        def saqlash(*a):
            if not ism_inp.text.strip():
                return
            app_data["hamkorlar"].append({
                "ism": ism_inp.text.strip(),
                "telefon": tel_inp.text.strip(),
                "qarzdorlik": float(qarz_inp.text or 0)
            })
            ma_lumot_saqlash(app_data)
            pop.dismiss()
            self._hamkorlarni_chiz()

        bekor = RangliTugma(rang=(0.85,0.85,0.9,1), matn_rangi=(0.3,0.3,0.35,1),
                            text="Bekor")
        bekor.bind(on_press=lambda x: pop.dismiss())
        saqla = RangliTugma(rang=RANGLAR["asosiy"], text="✅ Saqlash")
        saqla.bind(on_press=saqlash)
        tugmalar.add_widget(bekor)
        tugmalar.add_widget(saqla)
        asosiy.add_widget(tugmalar)

        pop.content = asosiy
        return pop

    def on_enter(self):
        self._qurish()

# ===================== SOZLAMALAR SAHIFASI =====================

class SozlamalarSahifasi(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._qurish()

    def _qurish(self):
        self.clear_widgets()
        asosiy = BoxLayout(orientation="vertical")

        yuqori = BoxLayout(size_hint_y=None, height=dp(60), padding=[dp(16), dp(10)])
        with yuqori.canvas.before:
            Color(*RANGLAR["asosiy"])
            bg = Rectangle(pos=yuqori.pos, size=yuqori.size)
        yuqori.bind(pos=lambda w, v: setattr(bg, 'pos', v),
                    size=lambda w, v: setattr(bg, 'size', v))
        yuqori.add_widget(Label(text="⚙️ Sozlamalar", font_size=dp(20), bold=True,
                                color=RANGLAR["oq"]))
        asosiy.add_widget(yuqori)

        scroll = ScrollView()
        kontent = BoxLayout(orientation="vertical", spacing=dp(12),
                            padding=[dp(16), dp(16)], size_hint_y=None)
        kontent.bind(minimum_height=kontent.setter("height"))

        sozlamalar = app_data.get("sozlamalar", {})

        kontent.add_widget(Label(text="Do'kon nomi", color=RANGLAR["kulrang"],
                                 size_hint_y=None, height=dp(28), halign="left",
                                 text_size=(Window.width, None)))
        self.dokon_nomi_inp = TextInput(
            text=sozlamalar.get("dokon_nomi", ""),
            hint_text="Do'kon nomini kiriting",
            multiline=False, size_hint_y=None, height=dp(48),
            font_size=dp(15), padding=[dp(12), dp(12)]
        )
        kontent.add_widget(self.dokon_nomi_inp)

        kontent.add_widget(Label(text="Egasining ismi", color=RANGLAR["kulrang"],
                                 size_hint_y=None, height=dp(28), halign="left",
                                 text_size=(Window.width, None)))
        self.egasi_inp = TextInput(
            text=sozlamalar.get("egasi", ""),
            hint_text="Ism Familiya",
            multiline=False, size_hint_y=None, height=dp(48),
            font_size=dp(15), padding=[dp(12), dp(12)]
        )
        kontent.add_widget(self.egasi_inp)

        saqlash_btn = RangliTugma(rang=RANGLAR["asosiy"], text="✅ Saqlash")
        saqlash_btn.bind(on_press=self.sozlamalarni_saqlash)
        kontent.add_widget(saqlash_btn)

        # Statistika
        kontent.add_widget(Widget(size_hint_y=None, height=dp(20)))
        kontent.add_widget(Label(text="📊 Statistika", font_size=dp(16), bold=True,
                                 color=RANGLAR["sarlavha"], size_hint_y=None, height=dp(36),
                                 halign="left", text_size=(Window.width, None)))

        jami_tranz = len(app_data["tranzaksiyalar"])
        jami_mij = len(app_data["mijozlar"])
        jami_ham = len(app_data["hamkorlar"])

        stat_matn = (f"📝 Jami tranzaksiyalar: {jami_tranz}\n"
                     f"👥 Jami mijozlar: {jami_mij}\n"
                     f"🤝 Jami hamkorlar: {jami_ham}")

        kontent.add_widget(Label(text=stat_matn, font_size=dp(14),
                                 color=RANGLAR["sarlavha"], size_hint_y=None,
                                 height=dp(80), halign="left",
                                 text_size=(Window.width - dp(32), None)))

        # Ma'lumotlarni tozalash
        kontent.add_widget(Widget(size_hint_y=None, height=dp(10)))
        tozalash_btn = RangliTugma(rang=RANGLAR["qizil"],
                                   text="🗑️ Barcha ma'lumotlarni o'chirish")
        tozalash_btn.bind(on_press=self.tozalash_tasdiqlash)
        kontent.add_widget(tozalash_btn)

        scroll.add_widget(kontent)
        asosiy.add_widget(scroll)
        self.add_widget(asosiy)

    def sozlamalarni_saqlash(self, *args):
        app_data["sozlamalar"]["dokon_nomi"] = self.dokon_nomi_inp.text.strip()
        app_data["sozlamalar"]["egasi"] = self.egasi_inp.text.strip()
        ma_lumot_saqlash(app_data)

        pop = Popup(title="✅ Saqlandi!", size_hint=(0.6, 0.25),
                    content=Label(text="Sozlamalar muvaffaqiyatli saqlandi!"))
        pop.open()

    def tozalash_tasdiqlash(self, *args):
        pop = Popup(title="⚠️ Diqqat!", size_hint=(0.85, 0.35))
        asosiy = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(16))
        asosiy.add_widget(Label(text="Barcha ma'lumotlar o'chiriladi!\nDavom etasizmi?",
                                color=RANGLAR["sarlavha"]))
        tugmalar = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(48))
        yoq = RangliTugma(rang=(0.6, 0.6, 0.65, 1), text="Yo'q")
        yoq.bind(on_press=lambda x: pop.dismiss())
        ha = RangliTugma(rang=RANGLAR["qizil"], text="Ha, o'chir")

        def tozala(*a):
            app_data["tranzaksiyalar"].clear()
            app_data["mijozlar"].clear()
            app_data["hamkorlar"].clear()
            ma_lumot_saqlash(app_data)
            pop.dismiss()

        ha.bind(on_press=tozala)
        tugmalar.add_widget(yoq)
        tugmalar.add_widget(ha)
        asosiy.add_widget(tugmalar)
        pop.content = asosiy
        pop.open()

    def on_enter(self):
        self._qurish()

# ===================== PASTKI NAVIGATSIYA =====================

class PastNaviPanel(BoxLayout):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        self.sm = sm
        self.size_hint_y = None
        self.height = dp(65)
        self.spacing = 0

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda w, v: setattr(self.bg, 'pos', v),
                  size=lambda w, v: setattr(self.bg, 'size', v))

        self.tugmalar = {}
        saxifalar = [
            ("bosh", "🏠", "Bosh"),
            ("mijozlar", "👥", "Mijozlar"),
            ("hamkorlar", "🤝", "Hamkorlar"),
            ("sozlamalar", "⚙️", "Sozlamalar"),
        ]

        for kod, belgi, nom in saxifalar:
            tugma = self._nav_tugma(kod, belgi, nom)
            self.tugmalar[kod] = tugma
            self.add_widget(tugma)

        self._faol_yangilash("bosh")

    def _nav_tugma(self, kod, belgi, nom):
        btn = BoxLayout(orientation="vertical", spacing=dp(2),
                        padding=[0, dp(8)])

        belgi_label = Label(text=belgi, font_size=dp(22), size_hint_y=None, height=dp(28))
        nom_label = Label(text=nom, font_size=dp(10), size_hint_y=None,
                          height=dp(16), color=RANGLAR["kulrang"])

        btn.add_widget(belgi_label)
        btn.add_widget(nom_label)

        btn._kod = kod
        btn._belgi = belgi_label
        btn._nom = nom_label

        btn.bind(on_touch_down=lambda w, t: self._bosish(w, t))
        return btn

    def _bosish(self, widget, touch):
        if widget.collide_point(*touch.pos):
            self.sm.current = widget._kod
            self._faol_yangilash(widget._kod)

    def _faol_yangilash(self, faol_kod):
        for kod, btn in self.tugmalar.items():
            if kod == faol_kod:
                btn._nom.color = RANGLAR["asosiy"]
                btn._belgi.color = RANGLAR["asosiy"]
            else:
                btn._nom.color = RANGLAR["kulrang"]
                btn._belgi.color = RANGLAR["kulrang"]

# ===================== ASOSIY ILOVA =====================

class DokonApp(App):
    def build(self):
        Window.clearcolor = RANGLAR["fon"]
        self.title = "Dokon Boshqaruv"

        asosiy = BoxLayout(orientation="vertical")

        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(BoshSahifa(name="bosh"))
        sm.add_widget(MijozlarSahifasi(name="mijozlar"))
        sm.add_widget(HamkorlarSahifasi(name="hamkorlar"))
        sm.add_widget(SozlamalarSahifasi(name="sozlamalar"))

        nav = PastNaviPanel(sm)

        asosiy.add_widget(sm)
        asosiy.add_widget(nav)

        return asosiy


if __name__ == "__main__":
    DokonApp().run()
