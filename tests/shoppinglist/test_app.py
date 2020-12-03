from pathlib import Path
from unittest.mock import patch, mock_open, Mock, call

import pytest

from shopping_list.app import App, main


@pytest.fixture
def mock_path():
    Path.exists = Mock()
    Path.exists.return_value = True
    return Path






@patch('builtins.input', side_effect=['0'])
@patch('builtins.print')
def test_app_sign_in(mocked_print, mocked_input):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    mocked_print.assert_any_call('*** SIGN IN ***')
    mocked_print.assert_any_call('0:\tExit')
    mocked_print.assert_any_call('Bye!')
    mocked_input.assert_called()


@patch('builtins.input', side_effect=['1', '<script>', 'ciccioRiccio99', 'ciccioRiccio9!'])
@patch('builtins.print')
def test_app_sign_in_resists_wrong_username(mocked_print, mocked_input):
    with patch('builtins.open', mock_open()):
        App().run()
    mocked_print.assert_any_call('*** SIGN IN ***')
    mocked_print.assert_any_call('*** SHOPPING LIST ***')


@patch('builtins.input', side_effect=['1', 'ciccioRiccio99', 'notSecurePassword', 'ciccioRiccio9!'])
@patch('builtins.print')
def test_app_sign_in_resists_wrong_password(mocked_print, mocked_input):
    with patch('builtins.open', mock_open()):
        App().run()
    mocked_print.assert_any_call('*** SIGN IN ***')
    mocked_print.assert_any_call('*** SHOPPING LIST ***')

@patch('builtins.input', side_effect=['1', 'ciccioRiccio19',   'ciccioRiccio9!'])
@patch('builtins.print')
def test_app_sign_in_nonexistent_user(mocked_print, mocked_input):
    with patch('builtins.open', mock_open()):
        App().run()
    mocked_print.assert_any_call('This user does not exist!')

@patch('builtins.input', side_effect=['2', 'ciccioRiccio99', 'ciccio@esiste.it',  'ciccioRiccio9!'])
@patch('builtins.print')
def test_app_registration_existent_user(mocked_print, mocked_input):
    with patch('builtins.open', mock_open()):
        App().run()
    mocked_print.assert_any_call('This user already exists!')


@patch('builtins.input', side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!'])
@patch('builtins.print')
def test_app_shopping_list(mocked_print, mocked_input):
    with patch('builtins.open', mock_open()):
        App().run()
    mocked_print.assert_any_call('*** SIGN IN ***')
    mocked_print.assert_any_call('1:\tLogin')
    mocked_print.assert_any_call('*** SHOPPING LIST ***')
    mocked_input.assert_called()


@patch('builtins.input', side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!'])
@patch('builtins.print')
def test_app_load_shopping_list(mocked_print, mocked_input):
    with patch('builtins.open', mock_open()):
        App().run()
    assert list(filter(lambda x: 'Smartphone' in str(x), mocked_print.mock_calls))
    mocked_input.assert_called()



@patch('builtins.input',
       side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!', '1', 'Redmi Note 8', 'Xiaomi', '2', '900', ''])
@patch('builtins.print')
def test_app_add_smartphone(mocked_print, mocked_input):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    assert list(filter(lambda x: 'Smartphone added!' in str(x), mocked_print.mock_calls))

@patch('builtins.input',
       side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!', '1', 'P40 pro', 'Huawei', '2', '900', '','1', 'P40 pro', 'Huawei', '2', '900', ''])
@patch('builtins.print')
def test_app_add_smartphone_with_duplicates(mocked_print, mocked_input):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    assert list(filter(lambda x: 'Smartphone already present in the list!' in str(x), mocked_print.mock_calls))


@patch('builtins.input',
       side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!', '1', '<script>', 'Mi 8 pro', 'Xiaomi', '2', '900', ''])
@patch('builtins.print')
def test_app_add_smartphone_resists_wrong_name(mocked_print, mocked_input):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    assert list(filter(lambda x: 'Smartphone added!' in str(x), mocked_print.mock_calls))


@patch('builtins.input',
       side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!', '1', 'Pocophone', 'Poco', 'asd', '-1', '2', '900', ''])
@patch('builtins.print')
def test_app_add_smartphone_resists_wrong_quantity(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    assert list(filter(lambda x: 'Smartphone added!' in str(x), mocked_print.mock_calls))



@patch('builtins.input',
       side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!', '1', 'Xperia z1', 'Sony', '2', 'asd', '-1', '900', ''])
@patch('builtins.print')
def test_app_add_smartphone_resists_wrong_price(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    assert list(filter(lambda x: 'Smartphone added!' in str(x), mocked_print.mock_calls))

@patch('builtins.input', side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!', '3', '1','3', '1','3', '1','3', '1','3', '1','3', '1','3', '1','3', '1','3', '1'])
@patch('builtins.print')
def test_app_remove_item(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    assert list(filter(lambda x: 'Item removed!' in str(x), mocked_print.mock_calls))

@patch('builtins.input', side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!','3','0'])
@patch('builtins.print')
def test_app_remove_item_operation_cancelled(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    assert list(filter(lambda x: 'Operation cancelled!' in str(x), mocked_print.mock_calls))

@patch('builtins.input', side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!','4','0'])
@patch('builtins.print')
def test_app_change_quantity_operation_cancelled(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    assert list(filter(lambda x: 'Operation cancelled!' in str(x), mocked_print.mock_calls))

@patch('builtins.input', side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!', '2', 'Mi Air', 'Xiaomi', '1', '400',
                                      'really excellent product'])
@patch('builtins.print')
def test_app_add_computer(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    assert list(filter(lambda x: 'Computer added!' in str(x), mocked_print.mock_calls))



@patch('builtins.input',
       side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!', '2', 'Macbook', 'Apple', '2', '1000', '', '2','Macbook', 'Apple', '2', '1000', ''])
@patch('builtins.print')
def test_app_add_computer_with_duplicates(mocked_print, mocked_input):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    assert list(filter(lambda x: 'Computer already present in the list!' in str(x), mocked_print.mock_calls))


@patch('builtins.input',
       side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!', '2', '<script>', 'Magicbook', 'Huawei', '5', '650.30', ''])
@patch('builtins.print')
def test_app_add_computer_resists_wrong_name(mocked_print, mocked_input):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    assert list(filter(lambda x: 'Computer added!' in str(x), mocked_print.mock_calls))


@patch('builtins.input',
       side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!', '2', 'Msv330', 'Msi', 'asd', '-1', '2', '900', ''])
@patch('builtins.print')
def test_app_add_computer_resists_wrong_quantity(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    assert list(filter(lambda x: 'Computer added!' in str(x), mocked_print.mock_calls))



@patch('builtins.input',
       side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!', '2', 'Sxs500v', 'Asus', '2', 'asd', '-1', '900', ''])
@patch('builtins.print')
def test_app_add_computer_resists_wrong_price(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    assert list(filter(lambda x: 'Computer added!' in str(x), mocked_print.mock_calls))






@patch('builtins.input', side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!', '3', '4', '1'])
@patch('builtins.print')
def test_app_remove_item_resists_wrong_index(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    mocked_input.assert_called()
    mocked_print.assert_called()
    assert list(filter(lambda x: 'Item removed!' in str(x), mocked_print.mock_calls))

@patch('builtins.input', side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!', '1','Pixel','Google','1','973.20','', '4', '1', '5'])
@patch('builtins.print')
def test_app_change_quantity(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    mocked_input.assert_called()
    mocked_print.assert_called()
    assert list(filter(lambda x: 'Quantity changed!' in str(x), mocked_print.mock_calls))

@patch('builtins.input', side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!', '4', '-1','1', '5'])
@patch('builtins.print')
def test_app_change_quantity_resists_wrong_index(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    mocked_input.assert_called()
    mocked_print.assert_called()
    assert list(filter(lambda x: 'Quantity changed!' in str(x), mocked_print.mock_calls))

@patch('builtins.input', side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!',  '4', '1', '-1','5'])
@patch('builtins.print')
def test_app_change_quantity_resists_wrong_new_quantity(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    mocked_input.assert_called()
    mocked_print.assert_called()
    assert list(filter(lambda x: 'Quantity changed!' in str(x), mocked_print.mock_calls))




@patch('builtins.input', side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!', '2','Mac','Apple','1','1','','6'])
@patch('builtins.print')
def test_app_sort_by_price(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    mocked_input.assert_called()
    mocked_print.assert_called()
    assert list(filter(lambda x: '1   Computer                       Mac' in str(x), mocked_print.mock_calls))



@patch('builtins.input', side_effect=['1', 'ciccioRiccio99', 'ciccioRiccio9!', '1','Ilprimo', 'AA', '2','50','', '5'])
@patch('builtins.print')
def test_app_sort_by_manufacturer(mocked_print, mocked_input, mock_path):
    with patch('builtins.open', mock_open()) as mocked_open:
        App().run()
    mocked_input.assert_called()
    mocked_print.assert_called()
    assert list(filter(lambda x: '1   Smartphone                     Ilprimo' in str(x), mocked_print.mock_calls))



# @patch('builtins.input', side_effect=['0'])
# @patch('builtins.print')
# def test_app_global_exception_handler(mocked_print, mocked_input):
#     with patch.object(Path, 'exists') as mocked_path_exits:
#         mocked_path_exits.side_effect = Mock(side_effect=Exception('Test'))
#         App().run()
#     assert mocked_input.mock_calls == []
#     assert list(filter(lambda x: 'Panic Error!' in str(x), mocked_print.mock_calls))
