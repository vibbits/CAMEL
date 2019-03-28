import click
import csv


def parse(input_file_name):
    '''
    Read a single row from the Excel csv file at a time and
    write it to the database;
    '''
    pass


@click.command()
@click.argument('input', 'input_file_name')
def main(input_file_name):
    '''
    Parse the original CAMEL input table from Excel and write the data
    into the new CAMEL database.

    INPUT: the original input file, exported from Excel as a CSV.
    
    '''
    parse(input_file_name)


if __name__ == '__main__':
    main()
