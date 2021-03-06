import pymysql
from geneticalgorithm.chromosome import create_random_chromosome
from inputOutput.sqlStatements import INSERT_INTO_SAVED_POPULATION, \
    INSERT_INTO_CHROMOSOMES, BEST_CHROMOSOMES_CREATE_STATEMENT, \
    WORST_CHROMOSOMES_CREATE_STATEMENT, MEDIAN_CHROMOSOMES_CREATE_STATEMENT, \
    TABLE_EXISTS_STRING, DROP_TABLE_STATEMENT, \
    GENETIC_ALGORITHM_TABLE_CREATE_STATEMENT, \
    CHROMOSOME_TABLE_CREATE_STATEMENT, \
    POPULATION_TABLE_CREATE_STATEMENT, INSERT_INTO_GENETIC_ALGORITHM, \
    INSERT_INTO_BEST_CHROMOSOMES, INSERT_INTO_WORST_CHROMOSOMES, \
    INSERT_INTO_MEDIAN_CHROMOSOMES, LIST_OF_TABLES

__author__ = 'snorre'


from easylogging import configLogger


class DbHandler(object):
    def __init__(self, hostname, database, username, password, port=3306):
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
        self.logger = configLogger.get_logger_for_stdout("DbHandler")
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.database = database

    def __getDatabaseConnection(self):
        try:
            con = pymysql.connect(host=self.hostname,
                                  port=self.port,
                                  db=self.database,
                                  user=self.username,
                                  passwd=self.password)
        except pymysql.Error:
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
        except pymysql.Error as e:
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
            except pymysql.Error:
                raise
        else:
            raise pymysql.Error(0, "Warning table {0} already exists".format(
                name))

    def drop_table(self, name):
        tableExist = self.tableExists(name)
        if tableExist:
            try:
                con = self.__getDatabaseConnection()
                cursor = con.cursor()
                cursor.execute(DROP_TABLE_STATEMENT % (name,))
                con.close()
            except pymysql.Error:
                raise

    def create_ga_table(self):
        try:
            self.create_table("genetic_algorithm",
                              GENETIC_ALGORITHM_TABLE_CREATE_STATEMENT)

        except pymysql.Error as e:
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
        except pymysql.Error as e:
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
        except pymysql.Error as e:
            self.logger.debug("Error {0:d}: {1:s}".format(e.args[0],
                                                          e.args[1]))
            return False
        else:
            self.logger.debug("Successfully created chromosomes table")
            return True

    def drop_saved_population_table(self):
        try:
            self.drop_table("saved_population")
        except pymysql.Error as e:
            self.logger.debug("Error {0:d}: {1:s}".format(e.args[0],
                                                          e.args[1]))
        else:
            self.logger.debug("Successfully dropped saved_population table")

    def create_best_chromosomes_table(self):
        try:
            self.create_table("best_chromosomes",
                              BEST_CHROMOSOMES_CREATE_STATEMENT)
        except pymysql.Error as e:
            self.logger.debug("Error {0:d}: {1:s}".format(e.args[0],
                                                          e.args[1]))
            return False
        else:
            self.logger.debug("Successfully created best_chromosomes table")
            return True

    def create_worst_chromosomes_table(self):
        try:
            self.create_table("worst_chromosomes",
                              WORST_CHROMOSOMES_CREATE_STATEMENT)
        except pymysql.Error as e:
            self.logger.debug("Error {0:d}: {1:s}".format(e.args[0],
                                                          e.args[1]))
            return False
        else:
            self.logger.debug("Successfully created worst_chromosomes table")
            return True

    def create_median_chromosomes_table(self):
        try:
            self.create_table("median_chromosomes",
                              MEDIAN_CHROMOSOMES_CREATE_STATEMENT)
        except pymysql.Error as e:
            self.logger.debug("Error {0:d}: {1:s}".format(e.args[0],
                                                          e.args[1]))
            return False
        else:
            self.logger.debug("Successfully created median_chromosomes table")
            return True

    def create_all_tables(self):
        self.create_ga_table()
        self.create_saved_population_table()
        self.create_chromosomes_table()
        self.create_best_chromosomes_table()
        self.create_worst_chromosomes_table()
        self.create_median_chromosomes_table()

    def insert_chromosomes_saved_population(self, chromosomes):
        values = []
        for chromosome in chromosomes:
            values.append(chromosome.chromosome_as_dict())

        sql = INSERT_INTO_SAVED_POPULATION

        con = self.__getDatabaseConnection()
        cur = con.cursor()
        cur.executemany(sql, values)
        con.commit()
        cur.close()
        con.close()

    def insert_chromosomes_chromosomes(self, chromosomes):
        values = []
        for chromosome in chromosomes:
            values.append(chromosome.chromosome_as_dict())

        sql = INSERT_INTO_CHROMOSOMES

        con = self.__getDatabaseConnection()
        cur = con.cursor()
        cur.executemany(sql, values)
        con.commit()
        cur.close()
        con.close()

    def insert_generation(self, generationResult):
        self.logger.debug("Inserting generation into database")
        sql = INSERT_INTO_GENETIC_ALGORITHM
        con = self.__getDatabaseConnection()
        cur = con.cursor()
        cur.execute(sql, generationResult)
        con.commit()
        cur.close()
        con.close()

    def insert_top_chromosomes(self, chromosomes, generation):
        self.insert_chromosomes_chromosomes(chromosomes)

        con = self.__getDatabaseConnection()
        cur = con.cursor()
        sql = INSERT_INTO_BEST_CHROMOSOMES
        values = []
        for chromosome in chromosomes:
            values.append([generation, chromosome.id])

        cur.executemany(sql, values)
        con.commit()
        cur.close()
        con.close()

    def insert_worst_chromosomes(self, chromosomes, generation):
        self.insert_chromosomes_chromosomes(chromosomes)
        con = self.__getDatabaseConnection()
        cur = con.cursor()
        sql = INSERT_INTO_WORST_CHROMOSOMES
        values = []
        for chromosome in chromosomes:
            values.append([generation, chromosome.id])

        cur.executemany(sql, values)
        con.commit()
        cur.close()
        con.close()

    def insert_median_chromosomes(self, chromosomes, generation):
        self.insert_chromosomes_chromosomes(chromosomes)

        con = self.__getDatabaseConnection()
        cur = con.cursor()
        sql = INSERT_INTO_MEDIAN_CHROMOSOMES
        values = []
        for chromosome in chromosomes:
            values.append([generation, chromosome.id])

        cur.executemany(sql, values)
        con.commit()
        cur.close()
        con.close()

    def drop_tables(self):
        for tableName in LIST_OF_TABLES:
            try:
                self.drop_table(tableName)
            except pymysql.Error as e:
                self.logger.debug("Could not drop table: {0}".format(
                    tableName))

    def tables_exists(self):
        existsNum = 0
        for tableName in LIST_OF_TABLES:
            try:
                exists = self.tableExists(tableName)
            except pymysql.Error as e:
                self.logger.debug("Error {0:d}: {1:s}"
                                  .format(e.args[0], e.args[1]))
            else:
                if exists:
                    existsNum += 1
        if existsNum == len(LIST_OF_TABLES):
            return True
        else:
            return False


if __name__ == '__main__':
    dbHandler = DbHandler("localhost", "ctcluster", "secret",
                          "ctcluster")
    dbHandler.create_all_tables()
    chromosomes = []
    for _ in range(10):
        chromosome = create_random_chromosome()
        chromosome.result = ((4, 54, 534),
                             (0.87, 0.34, 0.54),
                             (0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
                             (0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
                             (0.5, 0.5, 0.5, 0.5, 0.5, 0.5))
        chromosomes.append(chromosome)
    dbHandler.insert_chromosomes_chromosomes(chromosomes)