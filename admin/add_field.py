import click

def gather_data():
    data = {}
    data['title'] = input("Field header: ")
    return data


def write_data(data):
    print(data)

def main():
    data = gather_data()
    write_data(data)

if __name__ == '__main__':
    main()
