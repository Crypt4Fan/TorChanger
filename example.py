from torchanger import TorChanger


if __name__ == '__main__':
    changer = TorChanger('localhost', 9050, 9051, 'pass')
    print(f'Current IP: {changer.get_current_ip()}')
    print('Changing IP')
    changer.change_ip()
    print(f'Current IP: {changer.get_current_ip()}')
