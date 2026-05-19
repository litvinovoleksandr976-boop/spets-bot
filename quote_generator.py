from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import datetime, os, urllib.request, tempfile

# Use built-in Helvetica fonts (work on Linux/Railway)
# Arial -> Helvetica, Arial-Bold -> Helvetica-Bold

ORANGE = colors.HexColor("#E8761A")
NAVY   = colors.HexColor("#0F1B2D")
LIGHT  = colors.HexColor("#F7F8FA")
BORDER = colors.HexColor("#E2E6EA")
MUTED  = colors.HexColor("#7A8494")
WARM   = colors.HexColor("#FFF8F2")
GREEN  = colors.HexColor("#27AE60")
BLUE   = colors.HexColor("#2980B9")

DB = {
    "cctv": {
        "budget": {
            "title": "Базовий пакет відеоспостереження",
            "subtitle": "HiLook by Hikvision — надійний захист за розумні гроші",
            "items": [
                {"name":"HiLook by Hikvision IP Camera 5MP","desc":"Вулична IP-камера 5MP, ІЧ 30м, захист IP67","qty":4,"unit":55},
                {"name":"HiLook 4ch 4K NVR Recorder","desc":"4-канальний реєстратор 4K, H.265+, мобільний додаток","qty":1,"unit":89},
                {"name":"2TB Toshiba S300 Surveillance HDD","desc":"Жорсткий диск для запису 24/7, ~14 днів архіву","qty":1,"unit":97},
                {"name":"Hikvision S Deep Base (DS-1280)","desc":"Монтажна коробка для камер","qty":4,"unit":20},
                {"name":"Монтаж та налаштування CCTV","desc":"Повний монтаж, налаштування, інструктаж","qty":1,"unit":429},
            ],
            "products": [
                {
                    "icon": "📷",
                    "name": "HiLook IP Камера 5MP",
                    "brand": "HiLook by Hikvision",
                    "tagline": "Чітке зображення вдень і вночі",
                    "why": "Ця камера — ваші очі 24/7. Навіть якщо щось трапиться вночі, ви побачите хто це був.",
                    "specs": [
                        ("Роздільність", "5 Мегапікселів — видно обличчя та номери авто"),
                        ("Нічне бачення", "ІЧ підсвічування 30м — бачить у повній темряві"),
                        ("Захист", "IP67 — працює в дощ, сніг і мороз"),
                        ("Підключення", "Дротове — стабільний сигнал без перебоїв"),
                    ],
                    "color": BLUE,
                },
                {
                    "icon": "🖥️",
                    "name": "4K NVR Відеореєстратор + HDD 2TB",
                    "brand": "HiLook + Toshiba",
                    "tagline": "Мозок вашої системи безпеки",
                    "why": "Реєстратор зберігає всі відео. Якщо щось трапиться — ви завжди можете переглянути запис з телефону.",
                    "specs": [
                        ("Каналів", "4 камери одночасно"),
                        ("Архів", "До 14 днів запису на диску 2TB"),
                        ("Доступ", "Перегляд з телефону через безкоштовний додаток"),
                        ("Простота", "Зрозумілий інтерфейс — розбереться кожен"),
                    ],
                    "color": NAVY,
                },
            ],
        },
        "standard": {
            "title": "Стандартний пакет відеоспостереження",
            "subtitle": "Hikvision AcuSense — розумна система з AI-детекцією",
            "items": [
                {"name":"Hikvision IP AcuSense DarkFighter Camera","desc":"4MP, DarkFighter, AI-детекція людини/транспорту","qty":4,"unit":111},
                {"name":"Hikvision 4ch 4K NVR Recorder","desc":"4K, AcuSense, H.265+, мобільний додаток","qty":1,"unit":141},
                {"name":"2TB Toshiba S300 Surveillance HDD","desc":"Запис 24/7, ~30 днів відеоархіву","qty":1,"unit":97},
                {"name":"Hikvision S Deep Base (DS-1280)","desc":"Монтажна коробка для камер","qty":4,"unit":20},
                {"name":"Монтаж та налаштування CCTV","desc":"Повний монтаж, NVR, мобільний додаток, навчання","qty":1,"unit":429},
            ],
            "products": [
                {
                    "icon": "📷",
                    "name": "Hikvision AcuSense DarkFighter 4MP",
                    "brand": "Hikvision",
                    "tagline": "AI-камера що відрізняє людину від тварини",
                    "why": "Ця камера не просто записує — вона думає. Якщо зайде людина, ви отримаєте сповіщення. Якщо пробіжить кіт — ні. Менше хибних тривог, більше спокою.",
                    "specs": [
                        ("Роздільність", "4MP — видно обличчя з 10 метрів"),
                        ("AI-детекція", "Розрізняє людину, авто і тварину"),
                        ("Нічне бачення", "DarkFighter — кольорове зображення у темряві"),
                        ("Сповіщення", "Миттєво на телефон при виявленні людини"),
                    ],
                    "color": BLUE,
                },
                {
                    "icon": "🖥️",
                    "name": "Hikvision 4K NVR + HDD 2TB",
                    "brand": "Hikvision + Toshiba",
                    "tagline": "Розумний реєстратор з AI-аналітикою",
                    "why": "Зберігає відео місяць. Знайдіть будь-який момент за секунди — реєстратор сам покаже всі події з людьми.",
                    "specs": [
                        ("Архів", "До 30 днів запису на диску 2TB"),
                        ("Якість", "4K роздільність запису"),
                        ("Доступ", "Hik-Connect додаток — перегляд з будь-якої точки світу"),
                        ("Розширення", "Підтримує до 8 камер"),
                    ],
                    "color": NAVY,
                },
            ],
        },
        "premium": {
            "title": "Преміум пакет відеоспостереження",
            "subtitle": "Hikvision ColorVu 3K+ — найкраща якість зображення на ринку",
            "items": [
                {"name":"Hikvision IP Hybrid ColorVu 3K+ Camera","desc":"3K+, ColorVu — кольорове зображення вночі, AI-детекція","qty":4,"unit":204},
                {"name":"Hikvision 8ch 4K AcuSense NVR","desc":"8-канальний 4K, AI, розпізнавання облич, Hik-Connect","qty":1,"unit":233},
                {"name":"2TB Toshiba S300 Surveillance HDD","desc":"Запис 24/7, 30+ днів у високій роздільності","qty":1,"unit":97},
                {"name":"Hikvision S Deep Base (DS-1280)","desc":"Монтажна коробка для камер","qty":4,"unit":20},
                {"name":"Монтаж та налаштування CCTV (Преміум)","desc":"Огляд об'єкта, монтаж, тестування, навчання","qty":1,"unit":429},
            ],
            "products": [
                {
                    "icon": "📷",
                    "name": "Hikvision ColorVu 3K+ Hybrid Camera",
                    "brand": "Hikvision",
                    "tagline": "Повнокольорове зображення вночі без прожекторів",
                    "why": "Звичайні камери вночі показують чорно-білу картинку. Ця — повнокольорову. Ви бачите колір одягу, колір авто. Найкраща камера для ідентифікації людей.",
                    "specs": [
                        ("Роздільність", "3K+ — найчіткіша деталізація на ринку"),
                        ("Нічне бачення", "ColorVu — кольорове зображення 24 години на добу"),
                        ("AI", "Розпізнавання облич та номерних знаків"),
                        ("Звук", "Вбудований мікрофон — запис звуку"),
                    ],
                    "color": ORANGE,
                },
                {
                    "icon": "🖥️",
                    "name": "Hikvision 8ch 4K AcuSense NVR",
                    "brand": "Hikvision",
                    "tagline": "Преміум реєстратор з AI та розпізнаванням облич",
                    "why": "8 каналів, AI аналітика, розпізнавання облич. Знайдіть будь-яку людину у відеоархіві за секунди по фото.",
                    "specs": [
                        ("Каналів", "8 камер — ідеально для великих об'єктів"),
                        ("AI", "Розпізнавання облич та пошук по базі"),
                        ("Архів", "30+ днів у 4K якості"),
                        ("Хмара", "Резервне копіювання в хмару"),
                    ],
                    "color": NAVY,
                },
            ],
        },
    },
    "alarm": {
        "budget": {
            "title": "Бюджетний пакет сигналізації",
            "subtitle": "Ajax Starter Kit 1 — бездротовий захист за 1 день",
            "items": [
                {"name":"Ajax Hub Wireless Starter Kit 1 — White (AJA-23310)","desc":"Hub + 2x MotionProtect + DoorProtect + 2x брелок + HomeSiren","qty":1,"unit":284},
            ],
            "products": [
                {
                    "icon": "🔒",
                    "name": "Ajax Hub Wireless Starter Kit 1",
                    "brand": "Ajax Systems",
                    "tagline": "Повний комплект бездротової сигналізації",
                    "why": "Ajax — найкраща бездротова сигналізація в Європі. Встановлюється за 1 день без свердління. Якщо хтось зайде у ваш будинок або офіс — ви дізнаєтесь миттєво.",
                    "specs": [
                        ("Hub", "Центральна панель керування з SIM-картою та Ethernet"),
                        ("Датчики руху", "2x MotionProtect — захист кімнат від вторгнення"),
                        ("Датчик дверей", "DoorProtect — сповіщення при відкритті дверей/вікон"),
                        ("Брелоки", "2x SpaceControl — постановка/зняття з охорони"),
                        ("Сирена", "HomeSiren — гучна сирена всередині"),
                        ("Додаток", "Ajax app — управління з будь-якої точки світу"),
                    ],
                    "color": GREEN,
                },
            ],
        },
        "premium": {
            "title": "Розширений пакет сигналізації",
            "subtitle": "Ajax Starter Kit 3 — максимальний захист з вуличною сиреною",
            "items": [
                {"name":"Ajax Hub Wireless Starter Kit 3 — White (AJA-23337)","desc":"Hub + 2x MotionProtect + DoorProtect + StreetSiren + ReX","qty":1,"unit":300},
            ],
            "products": [
                {
                    "icon": "🔒",
                    "name": "Ajax Hub Wireless Starter Kit 3",
                    "brand": "Ajax Systems",
                    "tagline": "Розширений захист з вуличною сиреною",
                    "why": "Kit 3 — це Kit 1 плюс вулична сирена яку чутно за квартал. Ідеально для тих хто хоче максимальний ефект залякування зловмисників. Плюс підсилювач сигналу для великих приміщень.",
                    "specs": [
                        ("Hub", "Центральна панель з подвійним зв'язком SIM+Ethernet"),
                        ("Датчики руху", "2x MotionProtect — захист кімнат"),
                        ("Датчик дверей", "DoorProtect — захист входів"),
                        ("Вулична сирена", "StreetSiren — 105dB, чутно за квартал, IP55"),
                        ("Підсилювач", "ReX — збільшує зону покриття для великих площ"),
                        ("Сповіщення", "Push + SMS на всі телефони родини миттєво"),
                    ],
                    "color": GREEN,
                },
            ],
        },
    },
}

PROP_MAP = {"house":"Будинок/Квартира","office":"Офіс/Бізнес","shop":"Магазин","warehouse":"Склад/Майданчик"}
TYPE_MAP = {"cctv":"Відеоспостереження Hikvision","alarm":"Сигналізація Ajax","both":"Відеоспостереження + Сигналізація","unsure":"Система безпеки"}

def pick_data(ans):
    t = ans.get("type","cctv")
    cat = "alarm" if t=="alarm" else "cctv"
    if cat=="alarm":
        tier = "budget" if ans.get("budget")=="low" else "premium"
    else:
        b=ans.get("budget","mid"); s=ans.get("size","medium")
        if b=="low": tier="budget"
        elif b in("high","open"): tier="premium"
        else: tier="standard"
        if s=="large": tier="premium"
        if s=="small" and b=="low": tier="budget"
    return DB[cat][tier]

def S(name,**kw):
    d=dict(fontName="Helvetica",fontSize=9,leading=13); d.update(kw)
    return ParagraphStyle(name,**d)

def hdr_block(W):
    h=Table([[
        Paragraph("<font color='#E8761A'><b>SPETS</b></font> <font color='white'><b>SECURITY</b></font><br/><font color='#666666' size='7'>ALWAYS NEAR</font>",
                  S("hl",fontName="Helvetica-Bold",fontSize=18,textColor=colors.white,leading=24)),
        Paragraph("<font color='white'><b>Spets Security LTD</b></font><br/><font color='#888888'>1 Oakcroft Road, Chessington<br/>Surrey, KT9 1BD<br/>VAT: 455026800</font>",
                  S("hr",fontSize=8,textColor=colors.white,leading=13,alignment=TA_RIGHT)),
    ]],colWidths=[W*.5,W*.5])
    h.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),NAVY),
        ("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12),
        ("LEFTPADDING",(0,0),(0,-1),14),("RIGHTPADDING",(-1,0),(-1,-1),14),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    return h

def make_product_card(prod, W):
    col = prod["color"]
    specs = prod["specs"]

    # Заголовок картки
    header = Table([[
        Paragraph(f"<font color='white' size='18'>{prod['icon']}</font>",
                  S("pi",fontSize=18,textColor=colors.white,alignment=TA_CENTER)),
        Paragraph(f"<font color='white'><b>{prod['name']}</b></font><br/>"
                  f"<font color='#cccccc' size='8'>{prod['brand']}</font>",
                  S("pn",fontName="Helvetica-Bold",fontSize=12,textColor=colors.white,leading=16)),
    ]],colWidths=[20*mm,W-20*mm])
    header.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),col),
        ("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12),
        ("LEFTPADDING",(0,0),(0,-1),10),("LEFTPADDING",(1,0),(1,-1),10),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))

    # Tagline
    tagline = Table([[
        Paragraph(f"<b>{prod['tagline']}</b>",
                  S("tg",fontName="Helvetica-Bold",fontSize=11,textColor=col)),
    ]],colWidths=[W])
    tagline.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#F0F4F8")),
        ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("LEFTPADDING",(0,0),(-1,-1),14),
    ]))

    # Чому це вам потрібно
    why_block = Table([[
        Paragraph(f"<font color='#E8761A'><b>Чому це вам потрібно?</b></font><br/>{prod['why']}",
                  S("why",fontSize=9,leading=14,textColor=colors.HexColor("#1A1A2E"))),
    ]],colWidths=[W])
    why_block.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),WARM),
        ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("LEFTPADDING",(0,0),(-1,-1),14),("RIGHTPADDING",(0,0),(-1,-1),14),
    ]))

    # Характеристики
    spec_rows = []
    for k,v in specs:
        spec_rows.append([
            Paragraph(f"<b>{k}</b>",S("sk",fontName="Helvetica-Bold",fontSize=8,textColor=col)),
            Paragraph(v,S("sv",fontSize=9,textColor=colors.HexColor("#1A1A2E"))),
        ])
    spec_table = Table(spec_rows,colWidths=[35*mm,W-35*mm])
    spec_table.setStyle(TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),14),("RIGHTPADDING",(0,0),(-1,-1),14),
        ("LINEBELOW",(0,0),(-1,-2),0.5,BORDER),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.white,LIGHT]),
    ]))

    # Рамка навколо картки
    outer = Table([[header],[tagline],[why_block],[spec_table]],colWidths=[W])
    outer.setStyle(TableStyle([
        ("LINEAFTER",(0,0),(-1,-1),1,BORDER),
        ("LINEBEFORE",(0,0),(-1,-1),1,BORDER),
        ("LINEBELOW",(0,-1),(-1,-1),2,col),
    ]))
    return outer

def generate_quote_pdf(ans:dict)->str:
    name     = ans.get("name","Клієнт")
    data     = pick_data(ans)
    items    = data["items"]
    products = data["products"]
    prop     = PROP_MAP.get(ans.get("prop",""),"Об'єкт")
    sys_type = TYPE_MAP.get(ans.get("type",""),"Система безпеки")
    now      = datetime.datetime.now()
    date_str = now.strftime("%d.%m.%Y")
    qnum     = f"QU-{now.strftime('%Y%m%d%H%M%S')}"
    expiry   = (now+datetime.timedelta(days=7)).strftime("%d.%m.%Y")
    path     = f"quote_{name.replace(' ','_')}_{now.strftime('%H%M%S')}.pdf"

    doc = SimpleDocTemplate(path,pagesize=A4,leftMargin=15*mm,rightMargin=15*mm,topMargin=12*mm,bottomMargin=15*mm)
    W   = A4[0]-30*mm
    story=[]

    # ══ СТОРІНКА 1: ПРЕЗЕНТАЦІЯ ══════════════════════════
    story.append(hdr_block(W))
    story.append(HRFlowable(width=W,thickness=3,color=ORANGE,spaceAfter=10))

    # Персональний заголовок
    story.append(Paragraph(f"Персональна пропозиція для {name}",
                           S("pt",fontName="Helvetica-Bold",fontSize=16,textColor=NAVY,alignment=TA_CENTER,spaceAfter=2)))
    story.append(Paragraph(f"{data['title']}",
                           S("pst",fontName="Helvetica-Bold",fontSize=11,textColor=ORANGE,alignment=TA_CENTER,spaceAfter=2)))
    story.append(Paragraph(f"{data['subtitle']}",
                           S("ps",fontSize=9,textColor=MUTED,alignment=TA_CENTER,spaceAfter=12)))
    story.append(HRFlowable(width=W,thickness=1,color=BORDER,spaceAfter=12))

    # 3 переваги
    adv=Table([[
        Paragraph("✓  Офіційний дилер\nHikvision та Ajax в UK",S("a1",fontName="Helvetica-Bold",fontSize=9,textColor=NAVY,alignment=TA_CENTER)),
        Paragraph("✓  Гарантія на монтаж\n12 місяців",S("a2",fontName="Helvetica-Bold",fontSize=9,textColor=NAVY,alignment=TA_CENTER)),
        Paragraph("✓  Встановлення\nза 3-5 днів",S("a3",fontName="Helvetica-Bold",fontSize=9,textColor=NAVY,alignment=TA_CENTER)),
    ]],colWidths=[W/3,W/3,W/3])
    adv.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),WARM),
        ("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12),
        ("LEFTPADDING",(0,0),(-1,-1),8),
        ("LINEABOVE",(0,0),(-1,0),3,ORANGE),
        ("LINEAFTER",(0,0),(1,-1),0.5,BORDER),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
    ]))
    story.append(adv)
    story.append(Spacer(1,16))

    # Картки продуктів
    for prod in products:
        story.append(make_product_card(prod,W))
        story.append(Spacer(1,14))

    # Що відбуватиметься — процес роботи
    story.append(HRFlowable(width=W,thickness=1,color=BORDER,spaceAfter=10))
    story.append(Paragraph("Як проходить встановлення?",
                           S("wh",fontName="Helvetica-Bold",fontSize=12,textColor=NAVY,spaceAfter=8)))

    steps=Table([[
        Paragraph("<font color='#E8761A'><b>1</b></font><br/><b>Замовлення</b><br/><font color='#7A8494'>Ви підтверджуєте пропозицію та вносите 50% передоплату</font>",
                  S("s1",fontSize=9,leading=13,alignment=TA_CENTER)),
        Paragraph("<font color='#E8761A'><b>2</b></font><br/><b>Доставка</b><br/><font color='#7A8494'>Обладнання доставляється за 5-7 робочих днів</font>",
                  S("s2",fontSize=9,leading=13,alignment=TA_CENTER)),
        Paragraph("<font color='#E8761A'><b>3</b></font><br/><b>Монтаж</b><br/><font color='#7A8494'>Наші інженери встановлюють систему за 3-5 днів</font>",
                  S("s3",fontSize=9,leading=13,alignment=TA_CENTER)),
        Paragraph("<font color='#E8761A'><b>4</b></font><br/><b>Навчання</b><br/><font color='#7A8494'>Пояснюємо як користуватись системою та додатком</font>",
                  S("s4",fontSize=9,leading=13,alignment=TA_CENTER)),
    ]],colWidths=[W/4,W/4,W/4,W/4])
    steps.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),LIGHT),
        ("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12),
        ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
        ("LINEAFTER",(0,0),(2,-1),0.5,BORDER),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LINEABOVE",(0,0),(-1,0),2,ORANGE),
    ]))
    story.append(steps)
    story.append(Spacer(1,12))

    # CTA
    cta=Table([[
        Paragraph("Готові замовити? Зв'яжіться з нами!",
                  S("cta",fontName="Helvetica-Bold",fontSize=11,textColor=colors.white,alignment=TA_CENTER)),
        Paragraph("+447706906079  |  r.brain@spetstech.co.uk",
                  S("ctac",fontSize=10,textColor=ORANGE,alignment=TA_CENTER)),
    ]],colWidths=[W*.5,W*.5])
    cta.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),NAVY),
        ("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12),
        ("LEFTPADDING",(0,0),(-1,-1),10),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    story.append(cta)

    # ══ СТОРІНКА 2: КВОТАЦІЯ ══════════════════════════════
    story.append(PageBreak())
    story.append(hdr_block(W))
    story.append(HRFlowable(width=W,thickness=3,color=ORANGE,spaceAfter=5))

    strip=Table([[
        Paragraph("<b>КВОТАЦІЯ</b>",S("tt",fontName="Helvetica-Bold",fontSize=24,textColor=NAVY)),
        Paragraph(f"Квотація №: <b>{qnum}</b><br/>Дата: <b>{date_str}</b><br/>Дійсна до: <b>{expiry}</b>",
                  S("tr",fontSize=8,textColor=MUTED,leading=14,alignment=TA_RIGHT)),
    ]],colWidths=[W*.5,W*.5])
    strip.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),LIGHT),
        ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("LEFTPADDING",(0,0),(0,-1),14),("RIGHTPADDING",(-1,0),(-1,-1),14),
        ("LINEBELOW",(0,0),(-1,-1),0.5,BORDER)]))
    story.append(strip)

    parties=Table([[
        Paragraph(f"<font color='#E8761A' size='7'><b>ПІДГОТОВЛЕНО ДЛЯ</b></font><br/><b>{name}</b><br/><font color='#7A8494'>{prop}<br/>Великобританія</font>",S("p1",leading=14)),
        Paragraph("<font color='#E8761A' size='7'><b>ПІДГОТОВЛЕНО</b></font><br/><b>Spets Security LTD</b><br/><font color='#7A8494'>1 Oakcroft Road, Chessington<br/>Surrey, KT9 1BD<br/>r.brain@spetstech.co.uk<br/>+447706906079</font>",S("p2",leading=14)),
    ]],colWidths=[W*.5,W*.5])
    parties.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("LEFTPADDING",(0,0),(-1,-1),14),("LINEAFTER",(0,0),(0,-1),0.5,BORDER),
        ("LINEBELOW",(0,0),(-1,-1),0.5,BORDER),("VALIGN",(0,0),(-1,-1),"TOP")]))
    story.append(parties)

    scope_t=(f"Spets Security LTD здійснить постачання та налаштування системи {sys_type} "
             f"на об'єкті клієнта ({prop}). Все обладнання буде встановлено кваліфікованими "
             f"інженерами. Система буде повністю введена в експлуатацію з мобільним додатком. "
             f"Гарантія на всі роботи — 12 місяців.")
    scope=Table([[Paragraph(f"<font color='#E8761A' size='7'><b>ОПИС РОБІТ</b></font><br/>{scope_t}",S("sc",leading=14))]],colWidths=[W])
    scope.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),WARM),
        ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("LEFTPADDING",(0,0),(-1,-1),14),("RIGHTPADDING",(0,0),(-1,-1),14),
        ("LINEBELOW",(0,0),(-1,-1),0.5,colors.HexColor("#FDE6CC"))]))
    story.append(scope)
    story.append(Spacer(1,4))

    cw=[8*mm,W-8*mm-18*mm-24*mm-24*mm-24*mm,18*mm,24*mm,24*mm,24*mm]
    def th(txt,al=TA_LEFT): return Paragraph(f"<font color='white' size='8'><b>{txt}</b></font>",S("th",fontName="Helvetica-Bold",alignment=al))
    td=[[th("#"),th("ОПИС ПОЗИЦІЇ"),th("КІЛ.",TA_CENTER),th("ЦІНА £",TA_RIGHT),th("ПДВ £",TA_RIGHT),th("РАЗОМ £",TA_RIGHT)]]
    sub=0
    for i,it in enumerate(items,1):
        net=it["qty"]*it["unit"]; vat=round(net*.2,2); tot=net+vat; sub+=net
        td.append([
            Paragraph(f"<font color='#E8761A'><b>{i}</b></font>",S("n",fontName="Helvetica-Bold",alignment=TA_CENTER)),
            Paragraph(f"<b>{it['name']}</b><br/><font color='#7A8494' size='8'>{it['desc']}</font>",S("d",leading=13)),
            Paragraph(str(it["qty"]),S("q",alignment=TA_CENTER)),
            Paragraph(f"£{it['unit']:.2f}",S("pr",alignment=TA_RIGHT)),
            Paragraph(f"£{vat:.2f}",S("vr",alignment=TA_RIGHT)),
            Paragraph(f"<b>£{tot:.2f}</b>",S("tr2",fontName="Helvetica-Bold",alignment=TA_RIGHT)),
        ])
    tbl=Table(td,colWidths=cw,repeatRows=1)
    tbl.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),
        ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
        ("LINEBELOW",(0,1),(-1,-1),0.5,BORDER),("VALIGN",(0,0),(-1,-1),"TOP"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,LIGHT])]))
    story.append(tbl)

    vt=round(sub*.2,2); gr=sub+vt
    tots=Table([
        ["",Paragraph("Сума без ПДВ:",S("tl",textColor=MUTED)),Paragraph(f"£{sub:.2f}",S("tv",alignment=TA_RIGHT))],
        ["",Paragraph("ПДВ (20%):",S("tl2",textColor=MUTED)),Paragraph(f"£{vt:.2f}",S("tv2",alignment=TA_RIGHT))],
        ["",Paragraph("<font color='white'><b>ЗАГАЛЬНА СУМА</b></font>",S("gl",fontName="Helvetica-Bold",fontSize=11,textColor=colors.white)),
             Paragraph(f"<font color='#E8761A'><b>£{gr:.2f}</b></font>",S("gv",fontName="Helvetica-Bold",fontSize=15,textColor=ORANGE,alignment=TA_RIGHT))],
    ],colWidths=[W*.55,W*.25,W*.2])
    tots.setStyle(TableStyle([("LINEABOVE",(0,0),(-1,0),1.5,BORDER),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
        ("BACKGROUND",(0,2),(-1,2),NAVY),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    story.append(tots)
    story.append(Spacer(1,6))

    bot=Table([[
        Paragraph("<font color='#E8761A' size='7'><b>ПЛАТІЖНІ РЕКВІЗИТИ</b></font><br/><b>Lloyds Bank</b><br/><font color='#7A8494'>Рахунок: 48253368<br/>Sort code: 30-99-50<br/>IBAN: GB38LOYD30995048253368<br/>BIC: LOYDGB21287</font>",S("b1",leading=13)),
        Paragraph("<font color='#E8761A' size='7'><b>УМОВИ</b></font><br/><font color='#7A8494'>1. Ціни дійсні <b>1 тиждень</b><br/>2. Доставка: <b>5-7 робочих днів</b><br/>3. Монтаж: <b>3-5 днів</b><br/>4. Гарантія на монтаж 12 міс.<br/>5. Передоплата 50% при замовленні</font>",S("b2",leading=13)),
    ]],colWidths=[W*.5,W*.5])
    bot.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("LEFTPADDING",(0,0),(-1,-1),14),("LINEAFTER",(0,0),(0,-1),0.5,BORDER),
        ("LINEABOVE",(0,0),(-1,0),0.5,BORDER),("VALIGN",(0,0),(-1,-1),"TOP")]))
    story.append(bot)

    ft=Table([[Paragraph("Spets Security LTD · VAT: 455026800 · r.brain@spetstech.co.uk · +447706906079",S("ft",fontSize=7,textColor=MUTED,alignment=TA_CENTER))]],colWidths=[W])
    ft.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),NAVY),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
    story.append(Spacer(1,4))
    story.append(ft)

    doc.build(story)
    return path
