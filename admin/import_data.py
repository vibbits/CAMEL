import click
import csv
import MySQLdb
import getpass
import sys

def db_connect(host, user, passwd, db):
    try:
        db = MySQLdb.connect(host=host,
                             user=user,
                             passwd=passwd,
                             db=db
        )
    except:
        print("Can't connect to database")
        sys.exit(1)
    
    return db


def parse(input_file_name, field_map, db):
    '''
    Read a single row from the Excel csv file at a time and
    write it to the database;
    '''
    with open(input_file_name) as input_file:
        data = csv.DictReader(input_file, dialect="excel")
        for row in data:
            experimentName = row['OverarchingExperiment']
            if not experimentName:
                ## TODO: distill exp name out of species/year 
                pass

            c = db.cursor
            sql = "INSERT INTO `experiments` (`name`) VALUES (%s)"
            c.execute(sql, (experimentName,))
            experiment_id = c.lastrowid
            c.close()
            
            authors = []
            for colName in row:
                if colName.isdigit():
                    authors.append(row[colName])
                elif colName in field_map['fields']:
                    c = db.cursor()
                    sql = "INSERT INTO `experiments_fields` (`experiment_id`, `field_id`, {}) VALUES (%s, %s, %s)".format(col_type)
                    c.execute(sql, (experiment_id, field_map['fields'][colName]), row[colName])
                    c.close()
                elif colName in field_map['references']:
                    ##collect reference data
                    pass

            
            

def load_field_map(mapping_file_name, db):
    field_map = {}
    field_map['fields'] = {}
    field_map['groups'] = {}
    field_map['references'] = {}
    with open(mapping_file_name) as mapping_file:
        for line in mapping_file:
            (table, excel_header, field_name) = line.strip().split('\t')

            if table == 'fields':
                ## TODO: also get column type
                c = db.cursor()
                sql = "SELECT id from `fields` WHERE `title` = %s"
                c.execute(sql, (field_name,))
                field_id = c.fetchone()[0]
                field_map['fields'][excel_header] = field_id
                c.close()
            elif table == 'groups':
                c = db.cursor()
                sql = "SELECT id from `groups` WHERE `title` = %s"
                c.execute(sql, (field_name,))
                field_id = c.fetchone()[0]
                field_map['groups'][excel_header] = field_id
                c.close()
            else:                
                field_map['references'][excel_header] = field_name
            
    return field_map

@click.command()
@click.argument('input_file_name','input',
              type=click.Path(exists=True)
)
@click.option('-f', '--fields', 'field_names',
              help="TAB delimited mapping between db fields and excel headers",
              type=click.Path(exists=True),
              required = True
)
@click.option('-h', '--host', 'db_host',
              help="Database server hostname",
              required = True
)
@click.option('-u', '--user', 'db_user',
              help="Database username"
)
@click.option('-p', '--password', 'db_passwd',
              help="Database password"
)
@click.option('-d', '--db', 'db_name',
              help="Database name (default: CAMEL)",
              default="CAMEL"
)
def main(input_file_name, field_names, db_host, db_user, db_name, db_passwd):
    '''
    Parse the original CAMEL input table from Excel and write the data
    into the CAMEL database.

    INPUT: the original input file, exported from Excel as a CSV.
    

    '''
    if not db_user:
        db_user = getpass.getuser()
    if not db_passwd:        
        db_passwd = getpass.getpass()
    db = db_connect(db_host, db_user, db_passwd, db_name)

    field_map = load_field_map(field_names, db)
    parse(input_file_name, field_map, db)
    
    db.close()


if __name__ == '__main__':
    main()
