from getpass import getpass
from wsgiref import headers

import csv
import sys
from pathlib import Path
from typing import Tuple, Callable, Any
import requests

from valid8 import validate, ValidationError

from shopping_list.domain import ShoppingList, Smartphone, Computer, Name, Manufacturer, Quantity, Price, Description, \
    Username, \
    Password, Email
from shopping_list.menu import Menu, MenuDescription, Entry

api_server = 'http://localhost:8000/api/v1/'


class App:
    __filename = Path(__file__).parent.parent / 'shoppingList.csv'
    __delimiter = '\t'
    __logged = False
    __key = None
    __id_dictionary = []

    def __init__(self):
        self.__first_menu = self.init_first_menu()
        self.__menu = self.__init_shopping_list_menu()
        self.__shoppinglist = ShoppingList()

    def init_first_menu(self) -> Menu:
        return Menu.Builder(MenuDescription('SIGN IN'), auto_select=lambda: print('Welcome!')) \
            .with_entry(Entry.create('1', 'Login', is_logged=lambda: self.__login())) \
            .with_entry(Entry.create('2', 'Register', on_selected=lambda: self.__register())) \
            .with_entry(Entry.create('0', 'Exit', on_selected=lambda: print('Bye!'), is_exit=True)) \
            .build()

    def __init_shopping_list_menu(self) -> Menu:
        return Menu.Builder(MenuDescription('SHOPPING LIST'), auto_select=lambda: self.__print_items()) \
            .with_entry(Entry.create('1', 'Add Smartphone', on_selected=lambda: self.__add_smartphone())) \
            .with_entry(Entry.create('2', 'Add Computer', on_selected=lambda: self.__add_computer())) \
            .with_entry(Entry.create('3', 'Remove Item', on_selected=lambda: self.__remove_item())) \
            .with_entry(Entry.create('4', 'Change quantity', on_selected=lambda: self.__change_quantity())) \
            .with_entry(Entry.create('5', 'Sort by Manufacturer', on_selected=lambda: self.__sort_by_manufacturer())) \
            .with_entry(Entry.create('6', 'Sort by Price', on_selected=lambda: self.__sort_by_price())) \
            .with_entry(Entry.create('0', 'Exit', on_selected=lambda: print('Bye!'), is_exit=True)) \
            .build()

    def __login(self) -> bool:
        username = self.__read("Username", Username)
        password = self.__read("Password", Password)
        res = requests.post(url=f'{api_server}auth/login/', data={'username': username, 'password': password})
        if res.status_code != 200:
            print('This user does not exist!')
            return False
        self.__key = res.json()['key']
        return True

    def __register(self) -> None:
        username = self.__read("Username", Username)
        email = self.__read("Email", Email)
        password = self.__read("Password", Password)

        res = requests.post(url=f'{api_server}auth/registration/',
                            data={'username': username, 'email': email, 'password1': password,
                                  'password2': password})
        if res.status_code == 400:
            print('This user already exists!')

    def __print_items(self) -> None:
        print_sep = lambda: print('-' * 200)
        print_sep()
        fmt = '%-3s %-30s %-30s %-30s %-30s %-30s %-50s'
        print(fmt % ('#', 'CATEGORY', 'NAME', 'MANUFACTURER', 'PRICE', 'QUANTITY', 'DESCRIPTION'))
        print_sep()
        for index in range(self.__shoppinglist.items()):
            item = self.__shoppinglist.item(index)
            print(fmt % (index + 1, item.category, item.name, item.manufacturer, item.price, item.quantity,
                         item.description))

        print_sep()

    def __add_smartphone(self) -> None:
        smartphone = Smartphone(*self.__read_item())
        try:
            self.__shoppinglist.add_smartphone(smartphone)
            self.__save(smartphone)
            print('Smartphone added!')
        except ValueError:
            print('Smartphone already present in the list!')

    def __add_computer(self) -> None:
        computer = Computer(*self.__read_item())
        try:
            self.__shoppinglist.add_computer(computer)
            self.__save(computer)
            print('Computer added!')
        except ValueError:
            print('Computer already present in the list!')

    def __remove_item(self) -> None:
        def builder(value: str) -> int:
            validate('value', int(value), min_value=0, max_value=self.__shoppinglist.items())
            return int(value)

        index = self.__read('Index (0 to cancel operation)', builder)
        if index == 0:
            print('Operation cancelled!')
            return
        self.__delete(self.__shoppinglist.item(index - 1))
        self.__shoppinglist.remove_item(index - 1)
        print('Item removed!')

    def __change_quantity(self) -> None:
        def builder(value: str) -> int:
            validate('value', int(value), min_value=0, max_value=self.__shoppinglist.items())
            return int(value)

        index = self.__read('Index (0 to cancel operation)', builder)
        if index == 0:
            print('Operation cancelled!')
            return

        quantity = self.__read('New Quantity', Quantity.cast)
        self.__shoppinglist.change_quantity(index - 1, quantity)
        self.__update(self.__shoppinglist.item(index - 1))
        print('Quantity changed!')

    def __sort_by_manufacturer(self) -> None:
        self.__shoppinglist.sort_by_manufacturer()

    def __sort_by_price(self) -> None:
        self.__shoppinglist.sort_by_price()

    def __run(self) -> None:
        while not self.__first_menu.run() == (True, False):
            try:
                self.__fetch()
            except ValueError as e:
                print('Continuing with an empty list of items...')
            self.__menu.run()

    def run(self) -> None:
        try:
            self.__run()
        except Exception as e:
            print(e)
            print('Panic error!', file=sys.stderr)

    def __fetch(self) -> None:
        res = requests.get(url=f'{api_server}shopping-list/', headers={'Authorization': f'Token {self.__key}'})

        if res.status_code != 200:
            return None
        json = res.json()
        for item in json:
            validate('row length', item, length=7)

            item_id = int(item['id'])
            name = Name(str(item['name']))
            category = str(item['category'])
            manufacturer = Manufacturer(str(item['manufacturer']))
            price = Price.create(int(int(item['price']) / 100), int(item['price']) % 100)
            quantity = Quantity(int(item['quantity']))

            self.__id_dictionary.append([item_id, name.value, manufacturer.value])

            description = Description(str(item['description']))

            if category == 'Smartphone':
                self.__shoppinglist.add_smartphone(Smartphone(name, manufacturer, price, quantity, description))
            elif category == 'Computer':
                self.__shoppinglist.add_computer(Computer(name, manufacturer, price, quantity, description))
            else:
                raise ValueError('Unknown item category in your shopping list')

    def __save(self, item: Any) -> None:
        req = requests.post(url=f'{api_server}shopping-list/add/',
                            headers={'Authorization': f'Token {self.__key}'},
                            data={'name': item.name.value, 'category': item.category,
                                  'manufacturer': item.manufacturer.value, 'price': item.price.value_in_cents,
                                  'quantity': item.quantity.value, 'description': item.description.value})

        self.__id_dictionary.append([req.json()['id'], item.name.value, item.manufacturer.value])

    def __update(self, item: Any) -> None:
        for i in range(len(self.__id_dictionary)):
            if (item.name.value, item.manufacturer.value) == (self.__id_dictionary[i][1], self.__id_dictionary[i][2]):
                requests.patch(url=f'{api_server}shopping-list/edit/{self.__id_dictionary[i][0]}',
                               headers={'Authorization': f'Token {self.__key}'}, data={'quantity': item.quantity.value})
                break

    def __delete(self, item: Any) -> None:
        index = None
        for i in range(len(self.__id_dictionary)):
            if (item.name.value, item.manufacturer.value) == (self.__id_dictionary[i][1], self.__id_dictionary[i][2]):
                requests.delete(url=f'{api_server}shopping-list/edit/{self.__id_dictionary[i][0]}',
                                headers={'Authorization': f'Token {self.__key}'})
                index = i
                break
        self.__id_dictionary.pop(index)

    @staticmethod
    def __read(prompt: str, builder: Callable) -> Any:
        while True:
            try:
                if prompt != 'Password':
                    line = input(f'{prompt}: ')
                else:
                    line = input(f'{prompt}: ')
                    # line = getpass(f'{prompt}: ')

                res = builder(line.strip())
                return res
            except (TypeError, ValueError, ValidationError) as e:
                print(e)

    def __read_item(self) -> Tuple[Name, Manufacturer, Price, Quantity, Description]:
        item = self.__read('Name', Name)
        manufacturer = self.__read('Manufacturer', Manufacturer)
        quantity = self.__read('Quantity', Quantity.cast)
        price = self.__read('Price', Price.parse)
        description = self.__read('Description', Description)
        return item, manufacturer, price, quantity, description


def main(name: str):
    if name == '__main__':
        App().run()


main(__name__)
