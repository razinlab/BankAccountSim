import random
import sqlite3

conn=sqlite3.connect("card.s3db")
cur=conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS card(
            id INTEGER,
            number TEXT, 
            pin TEXT,
            balance INTEGER DEFAULT 0
            );''')
conn.commit()

def luhn_checksum_digit(number):
    digits = [int(d) for d in number]
    for i in range(len(digits) - 1, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    checksum = sum(digits)
    return (10 - (checksum % 10)) % 10

def generate_16_digit_luhn_number():
    prefix = "400000"
    random_digits = "".join(str(random.randint(0, 9)) for _ in range(9))
    first_15_digits = prefix + random_digits
    checksum_digit = luhn_checksum_digit(first_15_digits)
    return first_15_digits + str(checksum_digit)


def is_luhn_valid(number):
    number_str = str(number)
    reversed_digits = number_str[::-1]
    total = 0
    for i, digit in enumerate(reversed_digits):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0

def generate_pin():
    pin = "".join(str(random.randint(0, 9)) for _ in range(4))
    return pin

def search_for_card(card_num, card_pin):
    cur.execute("SELECT number, pin FROM card WHERE number=? AND pin=?",(card_num,card_pin))
    conn.commit()
    results=cur.fetchone()
    if results:
        print('You have successfully logged in!')
    else:
        print('Wrong card number or PIN!')

def account_exists(transfer_card_num):
    cur.execute('SELECT EXISTS (SELECT 1 FROM card WHERE number=?)', (transfer_card_num,))
    conn.commit()
    account_exists_local = cur.fetchone()[0]
    return account_exists_local

def get_balance(card_num, card_pin):
    cur.execute("SELECT balance FROM card WHERE number=? AND pin=?",(card_num,card_pin))
    conn.commit()
    results=cur.fetchone()
    if results:
        balance = results[0]
        print(f'Balance: {balance}')

def add_income(card_num, card_pin, amount):
    cur.execute('''UPDATE card SET balance = balance + ?
                WHERE number=? AND pin = ?''',(amount, card_num, card_pin))
    conn.commit()
    print('Income was added!')

def check_card_errors(card_num,transfer_card_num):
    cur.execute('SELECT EXISTS (SELECT 1 FROM card WHERE number=?)', (transfer_card_num,))
    account_exists_local=cur.fetchone()[0]
    if card_num==transfer_card_num:
        print('You can\'t transfer money to the same account!')
        return False
    elif not is_luhn_valid(transfer_card_num):
        print('You probably made a mistake in the card number. Please try again!')
        return False
    elif not account_exists_local:
        print('Such a card does not exist.')
        return False
    else: return True

def check_balance(card_num, card_pin, amount):
    cur.execute('SELECT balance FROM card WHERE number=? AND pin=?', (card_num, card_pin))
    balance = cur.fetchone()[0]
    if int(balance) < int(amount):
        return False
    else: return True


def do_transfer(card_num, transfer_card_num, amount):
        cur.execute("UPDATE card SET balance = balance - ? WHERE number = ?", (amount, card_num))
        cur.execute('''UPDATE card SET balance = balance + ?
                        WHERE number=?''', (amount, transfer_card_num))
        conn.commit()
        print('Success!')


def delete_account(card_num, card_pin):
    cur.execute('DELETE FROM card where number=? and pin=?',(card_num,card_pin))
    conn.commit()
    print('Account was deleted!')

while True:
    print('1. Create an account\n'
          '2. Log into account\n'
          '0. Exit\n')
    selection=input()
    if selection == '1':
        current_card = generate_16_digit_luhn_number()
        current_pin = generate_pin()
        cur.execute('INSERT INTO card(number, pin, balance) VALUES (?, ?, ?)',
                    (current_card, current_pin, 0))
        conn.commit()
        print('Your account has been created:\n')
        print('Card Number:')
        print(current_card)
        print('PIN:')
        print(current_pin)
    elif selection == '2':
        print('Enter your card and pin:')
        input_card_number=str(input())
        input_pin=str(input())
        search_for_card(input_card_number, input_pin)
        print('1. Balance\n'
              '2. Add income\n'
              '3. Do transfer\n'
              '4. Close account\n'
              '5. Log out\n'
              '0. Exit\n')
        while True:
            selection=input()
            if selection == '1':
                get_balance(input_card_number, input_pin)
            elif selection == '2':
                deposit=int(input('Enter income: '))
                add_income(input_card_number, input_pin, deposit)
            elif selection == '3':
                transfer_num=input('Enter transfer number: ')
                if check_card_errors(input_card_number, transfer_num,):
                    transfer_amount=int(input('Enter transfer amount: '))
                    if not check_balance(input_card_number, input_pin, transfer_amount):
                        print('Not enough money!')
                    else:
                        do_transfer(input_card_number, transfer_num, transfer_amount)
            elif selection == '4':
                delete_account(input_card_number, input_pin)
            elif selection == '5':
                print('You have successfully logged out!')
                break
            elif selection == '0':
                exit()
    elif selection == '0':
        break
