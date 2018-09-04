from pyhive import hive
import sys
import pandas as pd
import os

def connect_hive(ip):
    return hive.connect(ip).cursor()

def data_clean(df):
	df.fillna(' ')
	df.applymap(lambda x : str(x).strip())
	return df

def file_to_csv(file_path, table_name, table_form, encode_type):
	if table_form == 'xls' or table_form =='xlsx':
		table = pd.read_excel(file_path, dtype = 'object')
	elif table_form == 'csv':
		table = pd.read_csv(file_path, dtype = 'object')
	columns = table.columns
	table = data_clean(table)
	table.to_csv(table_name+'_temp',index = False, encoding = encode_type)
	return columns

def sql(table_name_temp, table_name_input, column_type, file_path_temp):
	sql0 = """drop table if exists otemp.temp_load_%(table)s""" % {'table':table_name_temp}
	sql1 = """create table otemp.temp_load_%(table)s(%(input)s) row format delimited fields terminated by ',' tblproperties ('skip.header.line.count'='%(line)s')""" % {'table':table_name_temp, 'input':table_name_input, 'line': str(1-int(column_type))}
	sql2 = """ALTER TABLE otemp.temp_load_%(table)s  SET SERDEPROPERTIES ('serialization.encoding'='%(enco)s')""" % {'table':table_name_temp, 'enco': encode_type}
	sql3 = """LOAD DATA LOCAL INPATH '%(path)s' INTO TABLE otemp.temp_load_%(table)s""" % {'table':table_name_temp, 'path': file_path_temp}
	print(sql1)
	print(sql2)
	print(sql3)
	cursor.execute(sql0)
	cursor.execute(sql1)
	cursor.execute(sql2)
	os.system("""hive -e "%s;" """%(sql3))
	print("load %s was done!" %(file_path_temp))
	print("table name:")
	print('otemp.temp_load_'+table_name)
	print("column is:")
	print(table_name_input)


if __name__ == '__main__':             
	cur_path,encode_type,column_type  = sys.argv[1:]
	cursor = connect_hive('***')
	table_name, table_form = os.path.split(cur_path)[-1].split(".")
	file_path = os.path.join(os.getcwd(), cur_path)
	columns = file_to_csv(file_path, table_name, table_form, encode_type)
	table_name_temp = table_name + '_temp'
	file_path_temp = os.path.join(os.getcwd(), table_name_temp)
	if column_type == '0': 
	    table_name_input = ", ".join(map(lambda x: 'c'+ str(x)+ ' String' ,range(len(columns))))
	else:
	    table_name_input = ", ".join(map(lambda x: 'c'+ str(x)+ ' String' ,columns))
	sql(table_name_temp, table_name_input, column_type, file_path_temp)



