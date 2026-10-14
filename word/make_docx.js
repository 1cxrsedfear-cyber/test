// Simple beginner-style Word report: A4, Times New Roman 12, diagrams scaled to fit.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, ShadingType,
  AlignmentType, HeadingLevel, LevelFormat, BorderStyle, PageOrientation, Footer, PageNumber,
} = require("docx");

const HERE = __dirname;
const img = (n) => fs.readFileSync(path.join(HERE, n));
const FONT = "Times New Roman";
const PORTRAIT_W = 11906, PORTRAIT_H = 16838;          // A4 in DXA
const MARGIN = 1134;                                    // 2 cm
const CONTENT_W = PORTRAIT_W - 2 * MARGIN;              // 9638

// ---------- helpers ----------
const run = (text, o = {}) => new TextRun({ text, font: FONT, size: 22, ...o });
const p = (children, o = {}) =>
  new Paragraph({ spacing: { after: 80, line: 259 }, ...o, children: Array.isArray(children) ? children : [run(children)] });
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 200, after: 100 }, children: [run(t, { bold: true, size: 28 })] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 140, after: 60 }, children: [run(t, { bold: true, size: 24 })] });
const bold = (t) => run(t, { bold: true });
const bullet = (children) => new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40, line: 250 }, children: Array.isArray(children) ? children : [run(children)] });
const num = (ref, children) => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 40, line: 250 }, children: Array.isArray(children) ? children : [run(children)] });

const border = { style: BorderStyle.SINGLE, size: 4, color: "999999" };
const borders = { top: border, bottom: border, left: border, right: border };
const cell = (children, width, header = false) =>
  new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    shading: header ? { fill: "E7E6E6", type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: (Array.isArray(children) ? children : [children]).map((c) =>
      typeof c === "string" ? new Paragraph({ spacing: { after: 0 }, children: [run(c, { size: 20, bold: header })] }) : c),
  });
const table = (widths, head, rows) =>
  new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({ tableHeader: true, cantSplit: true, children: head.map((t, i) => cell(t, widths[i], true)) }),
      ...rows.map((r) => new TableRow({ cantSplit: true, children: r.map((t, i) => cell(t, widths[i])) })),
    ],
  });
const rich = (parts) => new Paragraph({ spacing: { after: 0 }, children: parts.map(([t, b]) => run(t, { size: 20, bold: !!b })) });
const picture = (file, w, h, alt) =>
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 80, after: 80 },
    children: [new ImageRun({ type: "png", data: img(file), transformation: { width: w, height: h }, altText: { title: alt, description: alt, name: alt } })],
  });

// ---------- page 1: stage 1 ----------
const page1 = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [run("Моделирование ПО", { size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [run("Регистрация на десктопе («Аэрофлот Бонус») в нотации BPMN", { bold: true, size: 30 })] }),

  h1("Этап 1. Кто участвует и границы процесса"),
  p("Я описал, как человек регистрируется на сайте «Аэрофлот Бонус» с компьютера. В процессе четыре участника (в BPMN они называются пулами):"),
  table([2700, 6938], ["Участник", "Что делает"], [
    ["Пользователь", "Заполняет форму мышью и клавиатурой, вводит код из SMS."],
    ["Веб-система Аэрофлот", [rich([["Это сам сайт. Внутри три дорожки: "], ["UI/UX", true], [" — то, что видит пользователь; "], ["AuthService", true], [" — сервер, который делает проверки; "], ["DataStore", true], [" — хранение данных."]])]],
    ["SMS-шлюз", "Внешняя система, которая присылает SMS с кодом."],
    ["База данных", "Хранит пользователей, коды и согласия."],
  ]),
  p([bold("Границы процесса. "), run("Старт — пользователь открыл страницу регистрации. Конец — он успешно вошёл в личный кабинет или получил финальное сообщение об ошибке.")], { spacing: { before: 140, after: 100 } }),

  h2("Глоссарий"),
  table([2900, 6738], ["Термин", "Что это значит"], [
    ["Валидация на лету", "Поле проверяется сразу, пока человек заполняет форму, а не после отправки."],
    ["Автофокус", "Курсор сам становится в первое поле, кликать не нужно."],
    ["Tab-навигация", "Переход между полями клавишей Tab."],
    ["Подсвечивание поля", "Поле с ошибкой выделяется, например красной рамкой."],
    ["Блокировка кнопки отправки", "Кнопка «Отправить» не нажимается, пока в форме есть ошибки."],
  ]),
  h1("Этап 2. Основная диаграмма"),
  p("Диаграмма — на следующей странице, читать её слева направо. Файл для редактора BPMN: registration_compact.bpmn."),
  h2("Что нарисовано на диаграмме"),
  bullet([bold("Задачи"), run(" (прямоугольники) — действия: открыть форму, автофокус, ввод данных, проверка поля (on blur), ошибка под полем, блокировка кнопки, проверка email, код, SMS, сохранение в БД.")]),
  bullet([bold("Шлюзы"), run(" (ромбы). С крестиком — выбор «да или нет»: «Поле валидно?», «Все поля валидны?», «Email уникален?», «Код верный?». С плюсом — две проверки одновременно (формат email и его уникальность).")]),
  bullet([bold("Сообщения"), run(" (пунктир) — обмен между участниками, например сайт просит SMS-шлюз прислать код. Внутри сайта между дорожками обычные стрелки — так правильно по BPMN.")]),
  bullet([bold("Данные"), run(" (листочки): форма регистрации, объект пользователя, код подтверждения, документ согласия.")]),
  bullet([bold("Граничные события"), run(" (кружки на краю задачи): таймаут кода и ошибка SMS-шлюза.")]),

  h2("Пять сценариев"),
  num("scen", [bold("Всё хорошо. "), run("Поля верны, email свободен, SMS пришло, код введён верно, пользователь сохранён, вход в кабинет.")]),
  num("scen", [bold("Ошибка в поле "), run("(формат, спецсимволы, слишком коротко). Под полем ошибка, кнопка заблокирована.")]),
  num("scen", [bold("Email уже есть "), run("(ответ сервера 409). Под полем сообщение, что email занят.")]),
  num("scen", [bold("Неверный код. "), run("Можно ввести код ещё раз; когда попытки кончились — финальная ошибка.")]),
  num("scen", [bold("Код просрочен. "), run("Срабатывает таймер, человек запрашивает новый код и получает новое SMS.")]),

];

// ---------- page 2 (landscape): stage 2 diagram ----------
const page2 = [
  new Paragraph({ spacing: { after: 60 }, children: [run("Основная диаграмма регистрации (читать слева направо)", { bold: true, size: 24 })] }),
  picture("registration_compact.png", 930, 566, "Основная BPMN-диаграмма регистрации"),
];

// ---------- page 3-4: legend, scenarios, stage 3 ----------
const page3 = [
  h1("Этап 3. Две небольшие диаграммы"),
  h2("Проверка полей (on blur)"),
  p("Когда человек уходит из поля, сайт проверяет, подходит ли значение по формату. Если нет — показывает ошибку под полем и подсвечивает поле красным. Если да — проверяет, что обязательное поле не пустое. В конце всегда обновляется состояние кнопки «Отправить». При нажатии «Отправить» проверка такая же, только для всех полей сразу."),
  picture("validation_simple.png", 600, 227, "Проверка полей"),
  h2("Согласия"),
  p("Сайт показывает галочки и ссылки на документы и проверяет, все ли обязательные поставлены. Если нет — кнопка блокируется и появляется подсказка «Примите условия». Если всё отмечено — кнопка разблокируется, согласия уходят на сервер, и там их записывают в базу данных с датой и типом."),
  picture("consents_simple.png", 600, 280, "Обработка согласий"),
];

// ---------- page 5: stage 4 ----------
const page4 = [
  h1("Этап 4. Требования и вывод"),
  h2("Нефункциональные требования"),
  p("Это требования не к тому, «что делает» сайт, а к тому, «как» он работает."),
  num("nfr", [bold("Доступность. "), run("У каждого поля есть подпись, текст ошибки хорошо виден, форму можно заполнить только с клавиатуры.")]),
  num("nfr", [bold("Скорость. "), run("Проверка поля работает сразу, без перезагрузки страницы.")]),
  num("nfr", [bold("Безопасность. "), run("Пароль хранят не как есть, а в виде хэша (password_hash).")]),
  num("nfr", [bold("Юридическое. "), run("Согласия сохраняют в базе с датой и типом.")]),
  num("nfr", [bold("Понятные ошибки. "), run("Если SMS не работает, пользователь видит понятное сообщение.")]),

  h2("Связь требований с диаграммой"),
  table([2600, 7038], ["Требование", "Где на диаграмме"], [
    ["1. Доступность", "Задачи «Открыть форму регистрации» (подписи полей), «Показать сообщение об ошибке под полем», «Ввод данных (с Tab-навигацией)»"],
    ["2. Скорость", "Задача «Валидация поля при потере фокуса (on blur)» и шлюз «Поле валидно?»"],
    ["3. Безопасность", "Задача «Сохранить пользователя в БД» (пароль как password_hash)"],
    ["4. Юридическое", "Задача «Записать Consent в БД с датой и типом» (диаграмма согласий)"],
    ["5. Понятные ошибки", "Граничное событие «SMS-шлюз недоступен» → задача «Показать понятное сообщение, предложить повторить позже»"],
  ]),

  h2("Граничные события"),
  p("Граничное событие — это кружок на краю задачи. Он срабатывает, если что-то пошло не так, и процесс уходит по запасному пути."),
  table([3000, 6638], ["Событие", "Что происходит"], [
    [[rich([["1. Таймаут ожидания кода", true]]), new Paragraph({ spacing: { after: 0 }, children: [run("часы на задаче «Ожидание ввода кода»", { size: 20, italics: true })] })],
      "Если человек не ввёл код вовремя, он нажимает «Запросить новый код», и сайт создаёт новый код и шлёт новое SMS."],
    [[rich([["2. Ошибка SMS-шлюза", true]]), new Paragraph({ spacing: { after: 0 }, children: [run("молния на задаче «Отправить SMS через шлюз»", { size: 20, italics: true })] })],
      "Если шлюз недоступен, сайт показывает понятное сообщение «попробуйте позже», а процесс заканчивается финальной ошибкой. Пользователь в базе не создаётся."],
  ]),

  h2("Вывод"),
  p("BPMN помогает просто и наглядно показать, кто и что делает при регистрации. Лучше всего на диаграмме видно проверку полей, блокировку кнопки и то, что происходит при ошибках. Фронтенд-разработчику это помогает понять, как должна вести себя форма. Бэкенд-разработчику — какие проверки и запросы нужны на сервере. UX-аналитику — увидеть, что каждое требование привязано к конкретной задаче и не забыто. Ещё один плюс: диаграмму можно открыть в редакторе BPMN и поправить."),
];

// ---------- document ----------
const footer = new Footer({
  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 20 })] })],
});
const portrait = { page: { size: { width: PORTRAIT_W, height: PORTRAIT_H }, margin: { top: 850, bottom: 850, left: MARGIN, right: MARGIN } } };
const landscape = { page: { size: { width: PORTRAIT_W, height: PORTRAIT_H, orientation: PageOrientation.LANDSCAPE }, margin: { top: 850, bottom: 700, left: 850, right: 850 } } };

const doc = new Document({
  creator: "Student",
  title: "Регистрация на десктопе (Аэрофлот Бонус) в BPMN",
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 30, bold: true }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 26, bold: true }, paragraph: { spacing: { before: 180, after: 80 }, outlineLevel: 1 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 567, hanging: 283 } } } }] },
      ...["scen", "nfr"].map((ref) => ({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 567, hanging: 340 } } } }] })),
    ],
  },
  sections: [
    { properties: portrait, footers: { default: footer }, children: page1 },
    { properties: landscape, footers: { default: footer }, children: page2 },
    { properties: portrait, footers: { default: footer }, children: [...page3, ...page4] },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  const out = path.join(HERE, "..", "aeroflot_registration_bpmn.docx");
  fs.writeFileSync(out, buf);
  console.log("written", out);
});
