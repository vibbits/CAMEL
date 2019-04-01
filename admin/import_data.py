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
            experimentId = row['ID']
            experimentName = row['OverarchingExperiment']

            ## TODO : add column!!!
            speciesName = row['Species']
            if not experimentName:
                ## TODO: distill exp name out of species/year 
                pass
            ## Check existing experiment name
            unique_name = False
            try_name = experimentName
            try_count = 0
            while not unique_name:
                sql = "SELECT count(*) from `experiments` WHERE `name` = %s"
                c = db.cursor
                c.execute(sql, (try_name,))
                exp_count = c.fetchone()[0]
                c.close()
                if exp_count == 0:
                    unique_name = True
                    experimentName = try_name
                else:
                    try_count += 1
                    try_name = "{}_{}".format(experimentName, try_count)
                                                
            c = db.cursor
            sql = "INSERT INTO `experiments` (`id`, `name`) VALUES (%s, %s)"
            c.execute(sql, (experimentId, experimentName))
            c.close()
            
            authors = []
            for colName in row:
                if colName in ['ID', 'OverarchingExperiment', 'Species']:
                    pass
                if colName.isdigit():
                    authors.append(row[colName])
                elif colName in field_map['fields']:
                    c = db.cursor()
                    field_id = field_map['fields'][colName]['id']
                    field_type = field_map['fields'][colName]['type']
                    sql = "INSERT INTO `experiments_fields` (`experiment_id`, `field_id`, `{}`) VALUES (%s, %s, %s)".format(field_type)
                    c.execute(sql, (experimentId, field_id, row[colName])
                    c.close()
                elif colName in field_map['groups']:
                    
                    pass
                elif colName in field_map['references']:
                    ##collect reference data
                    pass

            
            

def load_field_map(mapping_file_name, db):
    '''
    Create a dictionary for all available fields from a tab delimited file.

    Format: Type/Excel header/Field name

    fields: 
      Retrieve field id and value type
    groups:
      Retrieve group id
    references:
      
    
    '''
    field_map = {}
    field_map['fields'] = {}
    field_map['groups'] = {}
    field_map['references'] = {}
    with open(mapping_file_name) as mapping_file:
        for line in mapping_file:
            (table, excel_header, field_name) = line.strip().split('\t')

            if table == 'fields':
                c = db.cursor()
                sql = "SELECT id, type_column from `fields` WHERE `title` = %s"
                c.execute(sql, (field_name,))
                res = c.fetchone()
                field_id = res[0]
                field_type = res[1]
                field_map['fields'][excel_header] = {}
                field_map['fields'][excel_header]['id'] = field_id
                field_map['fields'][excel_header]['type'] = field_type
                c.close()
            elif table == 'groups':
                c = db.cursor()
                sql = "SELECT id from `groups` WHERE `title` = %s"
                c.execute(sql, (field_name,))
                field_id = c.fetchone()[0]
                field_map['groups'][excel_header] = {}
                field_map['groups'][excel_header]['id'] = field_id
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
