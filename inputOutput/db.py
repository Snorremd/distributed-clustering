__author__ = 'snorre'

import MySQLdb

DB_EXISTS_STRING = ("SELECT schema_name FROM information_schema.schemata WHERE"
                    "schema_name = %s")

TABLE_EXISTS_STRING = ("SELECT * FROM information_schema.tables WHERE table_"
                       "schema = %s AND table_name = %s LIMIT 1")

## SQL query to create chromosomes table
POPULATION_TABLE_CREATE_STATEMENT = \
    """
    CREATE TABLE IF NOT EXISTS `population` (
      `id` int NOT NULL AUTO_INCREMENT,
      `tree_type_1` int NOT NULL,
      `tree_type_2` double NOT NULL,
      `tree_type_3` double NOT NULL
      `top_base_clusters_amount` int(11) NOT NULL,
      `min_term_occurrence_collection` int(11) NOT NULL,
      `max_term_ratio_collection` int(11) NOT NULL,
      `min_limit_base_cluster_score` int(11) NOT NULL,
      `max_limit_base_cluster_score` int(11) NOT NULL,
      `drop_singleton_base_clusters` tinyint(1) NOT NULL,
      `drop_one_word_clusters` tinyint(1) NOT NULL,
      `fitness` double NOT NULL,
      PRIMARY KEY (id)

    ) ENGINE=InnoDB;
    """

GENETIC_ALGORITHM_TABLE_CREATE_STATEMENT = \
    """
    CREATE TABLE IF NOT EXISTS `genetic_algorithm` (
        `generation` int NOT NULL,
        `fitness_avg` double NOT NULL,
        `fmeasure_avg` double NOT NULL,
        `precision_avg` double NOT NULL,
        `recall_avg` double NOT NULL,
        `time_avg` int NOT NULL,
        `number_of_clusters_avg` int NOT NULL,
        `number_of_base_clusters_avg` int NOT NULL,
        `precision_avg_0` int NOT NULL,
        `precision_avg_1` int NOT NULL,
        `precision_avg_2` int NOT NULL,
        `precision_avg_3` int NOT NULL,
        `precision_avg_4` int NOT NULL,
        `precision_avg_5` int NOT NULL,
        `recall_avg_0` int NOT NULL,
        `recall_avg_1` int NOT NULL,
        `recall_avg_2` int NOT NULL,
        `recall_avg_3` int NOT NULL,
        `recall_avg_4` int NOT NULL,
        `recall_avg_5` int NOT NULL,
        `fmeasure_avg_0` int NOT NULL,
        `fmeasure_avg_1` int NOT NULL,
        `fmeasure_avg_2` int NOT NULL,
        `fmeasure_avg_3` int NOT NULL,
        `fmeasure_avg_4` int NOT NULL,
        `fmeasure_avg_5` int NOT NULL
        PRIMARY KEY (generation)
    ) ENGINE=InnoDB;
    """

CHROMOSOME_TABLE_CREATE_STATEMENT = \
    """
    CREATE TABLE IF NOT EXISTS `%s` (
        `id` int NOT NULL AUTO_INCREMENT,
        `tree_type_1` int NOT NULL,
        `tree_type_2` double NOT NULL,
        `tree_type_3` double NOT NULL
        `top_base_clusters_amount` int(11) NOT NULL,
        `min_term_occurrence_collection` int(11) NOT NULL,
        `max_term_ratio_collection` int(11) NOT NULL,
        `min_limit_base_cluster_score` int(11) NOT NULL,
        `max_limit_base_cluster_score` int(11) NOT NULL,
        `drop_singleton_base_clusters` tinyint(1) NOT NULL,
        `drop_one_word_clusters` tinyint(1) NOT NULL,
        `fitness` double NOT NULL,
        `fmeasure` double NOT NULL,
        `precision` double NOT NULL,
        `recall` double NOT NULL,
        `time` int NOT NULL,
        `number_of_clusters` int NOT NULL,
        `number_of_base_clusters` int NOT NULL,
        `precision_0` int NOT NULL,
        `precision_1` int NOT NULL,
        `precision_2` int NOT NULL,
        `precision_3` int NOT NULL,
        `precision_4` int NOT NULL,
        `precision_5` int NOT NULL,
        `recall_0` int NOT NULL,
        `recall_1` int NOT NULL,
        `recall_2` int NOT NULL,
        `recall_3` int NOT NULL,
        `recall_4` int NOT NULL,
        `recall_5` int NOT NULL,
        `f_measure_0` int NOT NULL,
        `f_measure_1` int NOT NULL,
        `f_measure_2` int NOT NULL,
        `f_measure_3` int NOT NULL,
        `f_measure_4` int NOT NULL,
        `f_measure_5` int NOT NULL
    )
    """


class DbHandler(object):
    def __init__(self, hostname, username, password, database, port=3306):
        """

        :param hostname: the host address of database (i.e. localhost/x.x.x.x)
        :type hostname: str
        :param port: the port that MySQL server listens to (default 3306)
        :type port: int
        :param username: the user name of db user
        :type username: str
        :param password: the password for user
        :type password: str
        :param database: the name of database to use
        :type database: str
        """
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.database = database

    def __getDatabaseConnection(self):
        try:
            con = MySQLdb.connect(host=self.hostname,
                                  port=self.port,
                                  database=self.database,
                                  user=self.username,
                                  password=self.password)
        except MySQLdb.Error:
            raise
        else:
            return con

    def tableExists(self, table):
        """
        :param table: name of table to check for
        :type table: str
        :rtype: bool
        :return: if the table exists
        """
        exists = False
        try:
            con = self.__getDatabaseConnection()
            cursor = con.cursor()
            cursor.execute(TABLE_EXISTS_STRING, (table,))
            result = cursor.fetchall()
            if len(result) > 0:
                exists = True
            con.close()
        except MySQLdb.Error, e:
            print "Error {0:d}: {1:s}".format(e.args[0],
                                              e.args[1])
        finally:
            return exists


if __name__ == '__main__':
    print "Creating dbhandler"
    dbhandler = DbHandler("localhost", "ctclustering", "test",
                          "ctclustering")
    print "Checking database"
    print dbhandler.tableExists("population")