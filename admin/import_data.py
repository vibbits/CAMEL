import click
import csv
import MySQLdb
import getpass
import sys
import re

def db_connect(host, user, passwd, db):
    try:
        db = MySQLdb.connect(host=host,
                             user=user,
                             passwd=passwd,
                             db=db,
                             charset='utf8'
        )
    except:
        print("Can't connect to database")
        sys.exit(1)
    
    return db


def parse(input_file_name, field_map, species_map, db):
    '''
    Read a single row from the Excel csv file at a time and
    write it to the database;
    '''
    with open(input_file_name) as input_file:
        data = csv.DictReader(input_file, dialect="excel")
        for row in data:
            experimentId = int(row['ID'])

            ## Store Experiment
            experimentName = row['OverarchingExperiment'].strip()
            if not experimentName:
                first_author = row['1'].strip()
                year = row['year'].strip()
                experimentName = first_author+"_"+year


            ## Check existing experiment name
            unique_name = False
            try_name = experimentName
            try_count = 0
            while not unique_name:
                sql = "SELECT count(*) from `experiments` WHERE `name` = %s"
                c = db.cursor()
                c.execute(sql, (try_name,))
                exp_count = c.fetchone()[0]
                c.close()
                if exp_count == 0:
                    unique_name = True
                    experimentName = try_name
                else:
                    try_count += 1
                    try_name = "{}_{}".format(experimentName, try_count)
                                                
            c = db.cursor()
            sql = "INSERT INTO `experiments` (`id`, `name`) VALUES (%s, %s)"
            c.execute(sql, (experimentId, experimentName))
            c.close()

            ## Link species            
            if experimentId in species_map:
                species_ids = species_map[experimentId]
                c = db.cursor()
                for species_id in species_ids:
                    sql = "INSERT INTO `experiments_species` (`experiment_id`, `species_id`) VALUES (%s, %s)"
                    c.execute(sql, (experimentId,species_id))                
                c.close()
            
            ## Add fields and references
            reference = {
                'authors': [],
                'title': '',
                'journal': '',
                'year': '',
                'pages': '',
                'url': ''
            }
            for colName in row:
                if colName in ['ID', 'OverarchingExperiment']:
                    pass
                elif colName in field_map['fields']:
                    raw_field_value = row[colName]
                    if raw_field_value and raw_field_value.upper() != 'NA':
                        field_id = field_map['fields'][colName]['id']
                        field_type = field_map['fields'][colName]['type']
                        field_unit = field_map['fields'][colName]['unit']

                        if field_type != "value_TEXT":
                            multiple_values = [v.strip() for v in re.split(', |and|AND', raw_field_value)]
                        else:
                            multiple_values = [raw_field_value]
                            
                        for field_value in multiple_values:
                            if field_unit:
                                ## Remove units when repeated inside the field
                                field_value = field_value.replace(field_unit, '')

                            if field_type == 'value_INT' or field_type == 'value_BOOL':
                                ## Fix borked scientific notations
                                scientific_pattern = '([0-9]+(\.[0-9]+)?x?)?10\^-?[0-9]+'
                                p = re.compile(scientific_pattern)
                                if p.fullmatch(field_value):
                                    field_value = field_value.replace('x10^', 'E')
                                    field_value = field_value.replace('10^', '1E')
                                    field_value = float(field_value)

                                field_value = int(field_value)
                            elif field_type == 'value_DOUBLE':
                                field_value = float(field_value)

                            c = db.cursor()
                            sql = "INSERT INTO `experiments_fields` (`experiment_id`, `field_id`, `{}`) VALUES (%s, %s, %s)".format(field_type)
                            c.execute(sql, (experimentId, field_id, field_value))
                            c.close()
                elif colName in field_map['groups']:
                    group_value = int(row[colName])
                    if group_value > 0:
                        c = db.cursor()
                        sql = "INSERT INTO `experiments_groups` (`experiment_id`,`group_id`, `active`) VALUES (%s, %s, %s)"
                        active = 1 if group_value == 1 else 0
                        c.execute(sql, (experimentId, field_map['groups'][colName]['id'], active))
                        c.close()
                elif colName.isdigit():
                    reference['authors'].append(row[colName].strip())
                elif colName in field_map['references']:
                    ref_field = field_map['references'][colName]
                    ref_value = row[colName].strip()
                    ## Strip out the ridiculous systemMessages some URLs seem to contain
                    p = re.compile('(https?://.*)\?systemMessage=')
                    match = p.match(ref_value)
                    if match:
                        ref_value = match.groups()[0]
                    reference[ref_field] = ref_value
                else:
                    raise ValueError('Unknown column header: {}'.format(colName))

            ## Insert gathered Reference info
            ## In our original data: assume every entry belongs to only one reference and vice versa
            reference['authors'] = ", ".join([a for a in reference['authors'] if a])
            c = db.cursor()
            sql = "INSERT INTO `references` (`authors`, `title`, `journal`, `year`, `pages`, `url`) VALUES (%s, %s, %s, %s, %s, %s)"
            c.execute(sql, (reference['authors'], reference['title'], reference['journal'], reference['year'], reference['pages'], reference['url']))
            new_ref_id = c.lastrowid;
            sql = "INSERT INTO `experiments_references` (`experiment_id`, `reference_id`) VALUES (%s, %s)"
            c.execute(sql, (experimentId, new_ref_id))
            c.close()

            db.commit()
            print("Imported experiment {} : {}".format(experimentId, experimentName))
                              
def load_species_map(species_map_file):
    '''
    In case of the original CAMEL data, the species
    and the join table (experiment_id -> species-id) are stored on 
    separate excel sheets. 
    By keeping the id's both for experiments and species, we can easily 
    reuse the foreign key mappings from the join table.
    '''
    with open(species_map_file) as species_file:
        species_file.readline() ##skip header
        exp_map = {}
        for line in species_file:
            (experiment_id, species_id) = line.strip().split('\t')
            experiment_id = int(experiment_id)
            species_id = int(species_id)
            if experiment_id not in exp_map:
                exp_map[experiment_id] = []
            exp_map[experiment_id].append(species_id)
        return exp_map


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
                sql = "SELECT id, unit, type_column from `fields` WHERE `title` = %s"
                c.execute(sql, (field_name,))
                res = c.fetchone()
                field_id = res[0]
                field_unit = res[1]
                field_type = res[2]
                field_map['fields'][excel_header] = {}
                field_map['fields'][excel_header]['id'] = field_id
                field_map['fields'][excel_header]['unit'] = field_unit
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
@click.option('-s', '--species', 'species_map_file',
              help="TAB delimited mapping from experiment_id to species_id",
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
def main(input_file_name, field_names, species_map_file, db_host, db_user, db_name, db_passwd):
    '''
    Parse the original CAMEL input table from Excel and write the data
    into the CAMEL database.

    INPUT: the original input file, exported from Excel as a CSV.
    
    Already in database: the species, fields and groups (loaded directly)

    '''
    if not db_user:
        db_user = getpass.getuser()
    if not db_passwd:        
        db_passwd = getpass.getpass()
    db = db_connect(db_host, db_user, db_passwd, db_name)

    field_map = load_field_map(field_names, db)
    species_map = load_species_map(species_map_file)
    parse(input_file_name, field_map, species_map, db)
    
    db.close()


if __name__ == '__main__':
    main()
