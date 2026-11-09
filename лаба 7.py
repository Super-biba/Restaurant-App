import sys
import tkinter as tk
from tkinter import messagebox as mb

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

MENU = {'Борщ с говядиной': 450, 'Стейк из лосося': 780, 'Паста Карбонара': 480,
        'Десерт Тирамису': 350, 'Кофе Капучино': 180}
NEW, CONFIRMED, COOKING, READY, INVOICED = (
    'Поступил новый заказ (Ожидает подтверждения)', 'Заказ проверен и подтвержден',
    'Отправлен на кухню (Готовится)', 'Заказ готов! Ожидает выставления счета', 'Счет выставлен администратором')
state = dict(items='', total=0, status='Корзина пуста', invoiced=False, paid=False, method='')

BOLD, NORMAL = ('Arial', 10, 'bold'), ('Arial', 10)


def header(parent, text, pady):
    tk.Label(parent, text=text, font=BOLD, bg='#ffffff', fg='#353b48').pack(anchor='w', padx=15, pady=pady)


def button(parent, text, cmd, bg, active, font=BOLD, **kw):
    return tk.Button(parent, text=text, command=cmd, font=font, bg=bg, fg='white', activebackground=active,
                     activeforeground='white', bd=0, height=2, cursor='hand2', **kw)


def textbox(parent, height):
    box = tk.Text(parent, height=height, width=42, font=NORMAL, bg='#f5f6fa', fg='#2f3640', bd=0,
                  highlightthickness=1, highlightbackground='#dcdde1')
    box.pack(padx=15, pady=2)
    return box


def show(box, text):
    box.config(state='normal')
    box.delete('1.0', tk.END)
    box.insert(tk.END, text)
    box.config(state='disabled')


class BeautifulRestaurantApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ИС 'Ресторан' — Лабораторная работа №7")
        self.geometry('780x460')
        self.configure(bg='#f5f6fa')
        self.resizable(False, False)
        self.cart = {}

        # ---- Экран клиента ----
        client = self.panel(' 🛒 ЭКРАН КЛИЕНТА ', 15)
        header(client, 'Электронное Меню:', 8)
        for name, price in MENU.items():
            row = tk.Frame(client, bg='#ffffff')
            row.pack(fill='x', padx=15, pady=3)
            tk.Label(row, text=f'• {name} — {price}р.', font=NORMAL, bg='#ffffff', fg='#2f3640').pack(side='left')
            tk.Button(row, text='+', font=('Arial', 9, 'bold'), width=3, bg='#f5f6fa', fg='#e1b12c',
                      activebackground='#e1b12c', activeforeground='white', bd=1, relief='groove',
                      command=lambda n=name, p=price: self.add_to_cart(n, p)).pack(side='right')
        header(client, 'Ваша корзина:', 5)
        self.cart_box = textbox(client, 5)
        self.cart_box.config(state='disabled')
        button(client, 'Оформить и отправить Заказ', self.send_order, '#4cd137', '#44bd32').pack(fill='x', padx=15, pady=8)
        button(client, 'Оплатить выставленный Счет', self.pay_order, '#00a8ff', '#0097e6').pack(fill='x', padx=15, pady=2)

        # ---- Панель администратора ----
        admin = self.panel(' 💼 ПАНЕЛЬ АДМИНИСТРАТОРА ', 405)
        header(admin, 'Мониторинг активного заказа:', 8)
        self.info_box = textbox(admin, 6)
        self.refresh()
        header(admin, 'Бизнес-логика управления:', 8)
        steps = (('1. Проверить и подтвердить Заказ', self.admin_confirm, '#718093', '#636e72'),
                 ('2. Направить заказ на Кухню', self.admin_kitchen, '#718093', '#636e72'),
                 ('3. Заказ готов — уведомить клиента', self.admin_ready, '#718093', '#636e72'),
                 ('4. Выставить Счет клиенту', self.admin_invoice, '#10ac84', '#0f9b76'))
        for text, cmd, bg, active in steps:
            button(admin, text, cmd, bg, active, font=('Arial', 9, 'bold')).pack(fill='x', padx=15, pady=4)

    def panel(self, title, x):
        frame = tk.LabelFrame(self, text=title, font=('Arial', 11, 'bold'), fg='#2f3640', bg='#ffffff',
                              bd=0, relief='flat')
        frame.place(x=x, y=15, width=360, height=430)
        return frame

    # ---- Клиент ----
    def add_to_cart(self, name, price):
        item = self.cart.setdefault(name, {'price': price, 'count': 0})
        item['count'] += 1
        lines = ''.join(f"• {n} x{d['count']} ({d['price'] * d['count']}р.)\n" for n, d in self.cart.items())
        total = sum(d['price'] * d['count'] for d in self.cart.values())
        show(self.cart_box, f'{lines}\nИтого к оплате: {total} руб.')

    def send_order(self):
        if not self.cart:
            return mb.showwarning('Внимание', 'Нельзя отправить пустой заказ! Сначала добавьте блюда.')
        state.update(items=', '.join(f"{n} x{d['count']}" for n, d in self.cart.items()),
                     total=sum(d['price'] * d['count'] for d in self.cart.values()),
                     status=NEW, invoiced=False, paid=False, method='')
        self.cart = {}
        self.refresh()
        mb.showinfo('Успех', 'Заказ успешно отправлен Администратору системы!')

    def ask_method(self):
        """Окно выбора способа оплаты: возвращает 'картой', 'наличными' или None."""
        dlg = tk.Toplevel(self, bg='#ffffff')
        dlg.title('Способ оплаты')
        dlg.geometry(f'300x190+{self.winfo_x() + 240}+{self.winfo_y() + 120}')
        dlg.resizable(False, False)
        dlg.transient(self)
        choice = []
        tk.Label(dlg, text=f"К оплате: {state['total']} руб.\nВыберите способ оплаты:", font=BOLD,
                 bg='#ffffff', fg='#353b48').pack(pady=15)
        for text, bg, active, method in (('💳 Картой', '#00a8ff', '#0097e6', 'картой'),
                                         ('💵 Наличными', '#10ac84', '#0f9b76', 'наличными')):
            button(dlg, text, lambda m=method: (choice.append(m), dlg.destroy()), bg, active).pack(fill='x', padx=30, pady=4)
        dlg.wait_visibility()
        dlg.grab_set()
        self.wait_window(dlg)
        return choice[0] if choice else None

    def pay_order(self):
        if not state['total']:
            return mb.showerror('Ошибка', 'У вас нет активных заказов для оплаты!')
        if not state['invoiced']:
            return mb.showwarning('Запрещено', 'Вы не можете оплатить заказ. Администратор еще не выставил вам счет!')
        if state['paid']:
            return mb.showinfo('Информация', 'Этот счет уже успешно оплачен.')
        method = self.ask_method()
        if not method:
            return
        state.update(paid=True, method=method, status='Заказ полностью оплачен. Чек закрыт ✅')
        self.refresh()
        mb.showinfo('Оплата', f"Счет на сумму {state['total']} руб. успешно оплачен {method}!")

    # ---- Администратор ----
    def refresh(self):
        if not self.cart and state['total']:  # клиент видит статус своего заказа
            show(self.cart_box, f"📦 Статус вашего заказа:\n{state['status']}")
        if not state['total']:
            return show(self.info_box, '🔄 Ожидание действий со стороны... ')
        pay = f"ОПЛАЧЕН ✅ ({state['method']})" if state['paid'] else 'ОЖИДАЕТ ОПЛАТЫ ❌'
        show(self.info_box, f"📋 Состав: {state['items']}\n💰 Сумма: {state['total']} руб.\n"
                            f"{'-' * 39}\n🚦 СТАТУС: {state['status']}\n💳 Оплата: {pay}")

    def advance(self, empty, src, dst, ok, bad):
        """Переводит заказ из статуса src в dst; иначе показывает сообщение bad = (тип, заголовок, текст)."""
        if not state['total']:
            return mb.showwarning('Ошибка', empty)
        if state['status'] != src:
            return getattr(mb, bad[0])(*bad[1:])
        state.update(status=dst, invoiced=state['invoiced'] or dst == INVOICED)
        self.refresh()
        mb.showinfo(*ok)

    def admin_confirm(self):
        self.advance('Нет поступающих заказов для подтверждения!', NEW, CONFIRMED,
                     ('Админ', 'Заказ успешно подтвержден!'),
                     ('showwarning', 'Действие отклонено', 'Этот заказ уже был проверен.'))

    def admin_kitchen(self):
        bad = (('showerror', 'Ошибка', 'Сначала подтвердите заказ кнопкой №1!') if state['status'] == NEW else
               ('showwarning', 'Действие отклонено', 'Заказ уже готовится или готов.'))
        self.advance('Нечего отправлять на кухню!', CONFIRMED, COOKING,
                     ('Кухня', 'Заказ передан поварам для исполнения!'), bad)

    def admin_ready(self):
        bad = (('showerror', 'Ошибка', 'Сначала отправьте заказ на кухню!') if state['status'] in (NEW, CONFIRMED) else
               ('showwarning', 'Действие отклонено', 'Заказ уже отмечен готовым.'))
        was_cooking = state['status'] == COOKING
        self.advance('Нет готовых заказов!', COOKING, READY, ('Кухня', 'Заказ готов! Клиент уведомлён.'), bad)
        if was_cooking:
            mb.showinfo('Ваш заказ', 'Ваш заказ готов! Приятного аппетита 🍽')

    def admin_invoice(self):
        bad = (('showwarning', 'Действие отклонено', 'Счет уже выставлен.') if state['invoiced'] else
               ('showerror', 'Ошибка', 'Нельзя выставить счет. Заказ должен сначала пройти кухню!'))
        self.advance('Невозможно выставить счет.', READY, INVOICED,
                     ('Счет выставлен', f"Счет на сумму {state['total']} руб. успешно выставлен!"), bad)


if __name__ == '__main__':
    BeautifulRestaurantApp().mainloop()
