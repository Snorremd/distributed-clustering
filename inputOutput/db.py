__author__ = 'snorre'

import MySQLdb
from easylogging import configLogger

DB_EXISTS_STRING = ("SELECT schema_name FROM information_schema.schemata WHERE"
                    "schema_name = %s")

TABLE_EXISTS_STRING = ("SELECT * FROM information_schema.tables WHERE table_"
                       "schema = %s AND table_name = %s LIMIT 1")

## SQL statement to
DROP_TABLE_STATEMENT = "DROP TABLE IF EXISTS %s"


## SQL statements to create tables
POPULATION_TABLE_CREATE_STATEMENT = \
    """
    CREATE TABLE IF NOT EXISTS `saved_population` (
      `id` int NOT NULL,
      `tree_type_1` int NOT NULL,
      `tree_type_2` double NOT NULL,
      `tree_type_3` double NOT NULL,
      `text_type_frontpageheading` tinyint NOT NULL,
      `text_type_frontpageintroduction` tinyint NOT NULL,
      `text_type_articleheading` tinyint NOT NULL,
      `text_type_articlebyline` tinyint NOT NULL,
      `text_type_articleintroduction` tinyint NOT NULL,
      `text_type_articletext` tinyint NOT NULL,
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
        `precision_avg_0` double NOT NULL,
        `precision_avg_1` double NOT NULL,
        `precision_avg_2` double NOT NULL,
        `precision_avg_3` double NOT NULL,
        `precision_avg_4` double NOT NULL,
        `precision_avg_5` double NOT NULL,
        `recall_avg_0` double NOT NULL,
        `recall_avg_1` double NOT NULL,
        `recall_avg_2` double NOT NULL,
        `recall_avg_3` double NOT NULL,
        `recall_avg_4` double NOT NULL,
        `recall_avg_5` double NOT NULL,
        `fmeasure_avg_0` double NOT NULL,
        `fmeasure_avg_1` double NOT NULL,
        `fmeasure_avg_2` double NOT NULL,
        `fmeasure_avg_3` double NOT NULL,
        `fmeasure_avg_4` double NOT NULL,
        `fmeasure_avg_5` double NOT NULL,
        PRIMARY KEY (generation)
    ) ENGINE=InnoDB;
    """

BEST_CHROMOSOMES_CREATE_STATEMENT = \
    """
    CREATE TABLE IF NOT EXISTS `best_chromosomes` (
        `generation_id` int NOT NULL,
        `chromosome_id` int NOT NULL,
        PRIMARY KEY (generation_id, chromosome_id),
        CONSTRAINT FOREIGN KEY (generation_id) REFERENCES genetic_algorithm(
        generation) ON DELETE CASCADE ON UPDATE CASCADE,
        CONSTRAINT FOREIGN KEY (chromosome_id) REFERENCES chromosomes(id)
        ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB;
    """

WORST_CHROMOSOMES_CREATE_STATEMENT = \
    """
    CREATE TABLE IF NOT EXISTS `worst_chromosomes` (
        `generation_id` int NOT NULL,
        `chromosome_id` int NOT NULL,
        PRIMARY KEY (generation_id, chromosome_id),
        CONSTRAINT FOREIGN KEY (generation_id) REFERENCES genetic_algorithm(
        generation)  ON DELETE CASCADE ON UPDATE CASCADE,
        CONSTRAINT FOREIGN KEY (chromosome_id) REFERENCES chromosomes(id)
        ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB;
    """

CHROMOSOME_TABLE_CREATE_STATEMENT = \
    """
    CREATE TABLE IF NOT EXISTS `chromosomes` (
        `id` int NOT NULL,
        `tree_type_1` int NOT NULL,
        `tree_type_2` double NOT NULL,
        `tree_type_3` double NOT NULL,
        `text_type_frontpageheading` tinyint NOT NULL,
        `text_type_frontpageintroduction` tinyint NOT NULL,
        `text_type_articleheading` tinyint NOT NULL,
        `text_type_articlebyline` tinyint NOT NULL,
        `text_type_articleintroduction` tinyint NOT NULL,
        `text_type_articletext` tinyint NOT NULL,
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
        `precision_0` double NOT NULL,
        `precision_1` double NOT NULL,
        `precision_2` double NOT NULL,
        `precision_3` double NOT NULL,
        `precision_4` double NOT NULL,
        `precision_5` double NOT NULL,
        `recall_0` double NOT NULL,
        `recall_1` double NOT NULL,
        `recall_2` double NOT NULL,
        `recall_3` double NOT NULL,
        `recall_4` double NOT NULL,
        `recall_5` double NOT NULL,
        `f_measure_0` double NOT NULL,
        `f_measure_1` double NOT NULL,
        `f_measure_2` double NOT NULL,
        `f_measure_3` double NOT NULL,
        `f_measure_4` double NOT NULL,
        `f_measure_5` double NOT NULL,
        PRIMARY KEY(id)
    ) ENGINE=InnoDB;
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
        self.logger = configLogger.getLoggerForStdOut("DbHandler")
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.database = database

    def __getDatabaseConnection(self):
        try:
            con = MySQLdb.connect(host=self.hostname,
                                  port=self.port,
                                  db=self.database,
                                  user=self.username,
                                  passwd=self.password)
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
            cursor.execute(TABLE_EXISTS_STRING, (self.database, table,))
            result = cursor.fetchall()
            if len(result) > 0:
                exists = True
            con.close()
        except MySQLdb.Error, e:
            self.logger.debug("Error {0:d}: {1:s}".format(e.args[0],
                                                          e.args[1]))
        else:
            return exists

    def create_table(self, name, statement):
        tableExist = self.tableExists(name)
        if not tableExist:
            try:
                con = self.__getDatabaseConnection()
                cursor = con.cursor()
                cursor.execute(statement)
                con.close()
            except MySQLdb.Error:
                raise
        else:
            raise MySQLdb.Error(0, "Warning table {0} already exists".format(
                name))

    def drop_table(self, name):
        tableExist = self.tableExists(name)
        if tableExist:
            try:
                con = self.__getDatabaseConnection()
                cursor = con.cursor()
                cursor.execute(DROP_TABLE_STATEMENT % (name,))
                con.close()
            except MySQLdb.Error:
                raise

    def create_ga_table(self):
        try:
            self.create_table("genetic_algorithm",
                              GENETIC_ALGORITHM_TABLE_CREATE_STATEMENT)

        except MySQLdb.Error, e:
            self.logger.debug("Error {0:d}: {1:s}".format(e.args[0],
                                                          e.args[1]))
            return False
        else:
            self.logger.debug("Successfully created genetic algorithm table")
            return True

    def create_chromosomes_table(self):
        try:
            self.create_table("chromosomes",
                              CHROMOSOME_TABLE_CREATE_STATEMENT)
        except MySQLdb.Error, e:
            self.logger.debug("Error {0:d}: {1:s}".format(e.args[0],
                                                          e.args[1]))
            return False
        else:
            self.logger.debug("Successfully created chromosomes table")
            return True

    def create_saved_population_table(self):
        try:
            self.create_table("saved_population",
                              POPULATION_TABLE_CREATE_STATEMENT)
        except MySQLdb.Error, e:
            self.logger.debug("Error {0:d}: {1:s}".format(e.args[0],
                                                          e.args[1]))
            return False
        else:
            self.logger.debug("Successfully created chromosomes table")
            return True

    def drop_saved_population_table(self):
        try:
            self.drop_table("saved_population")
        except MySQLdb.Error, e:
            self.logger.debug("Error {0:d}: {1:s}".format(e.args[0],
                                                          e.args[1]))
        else:
            self.logger.debug("Successully dropped saved_population table")

    def create_best_chromosomes_table(self):
        try:
            self.create_table("best_chromosomes",
                              BEST_CHROMOSOMES_CREATE_STATEMENT)
        except MySQLdb.Error, e:
            self.logger.debug("Error {0:d}: {1:s}".format(e.args[0],
                                                          e.args[1]))
            return False
        else:
            self.logger.debug("Successfully created chromosomes table")
            return True

    def create_worst_chromosomes_table(self):
        try:
            self.create_table("worst_chromosomes",
                              WORST_CHROMOSOMES_CREATE_STATEMENT)
        except MySQLdb.Error, e:
            self.logger.debug("Error {0:d}: {1:s}".format(e.args[0],
                                                          e.args[1]))
            return False
        else:
            self.logger.debug("Successfully created chromosomes table")
            return True

    def create_all_tables(self):
        self.create_ga_table()
        self.create_saved_population_table()
        self.create_chromosomes_table()
        self.create_best_chromosomes_table()
        self.create_worst_chromosomes_table()

    def insert_chromosomes_saved_population(self, chromosomes):
        values = []
        for chromosome in chromosomes:
            chromosomeDict = chromosome.chromosome_as_dict()
            values


    def insert_chromosome_chromosomes(self):
        pass

    def insert_generation(self):
        pass

    def insert_top_chromosome(self):
        pass

    def insert_worst_chromosome(self):
        pass


if __name__ == '__main__':
    dbhandler = DbHandler("localhost", "ctcluster", "fTnYTmuPm6FbEmZK",
                          "ctcluster")
    dbhandler.create_all_tables()