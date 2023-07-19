import yaml

file = open('config/db/db_config_pstgr.yaml', 'r')
data = yaml.safe_load(file)
file.close()

postgresql = data

postgresqlConfig = "postgresql://{}:{}@{}/{}".format(postgresql['user'], postgresql['passwd'], postgresql['host'], postgresql['db'])