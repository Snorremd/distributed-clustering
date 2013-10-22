__author__ = 'snorre'


LIST_OF_TABLES = [
    "best_chromosomes",
    "worst_chromosomes",
    "median_chromosomes",
    "genetic_algorithm",
    "chromosomes",
    "saved_population"
]

DB_EXISTS_STRING = ("SELECT schema_name FROM information_schema.schemata WHERE"
                    "schema_name = %s")

TABLE_EXISTS_STRING = ("SELECT * FROM information_schema.tables WHERE table_"
                       "schema = %s AND table_name = %s LIMIT 1")

DROP_TABLE_STATEMENT = "DROP TABLE IF EXISTS %s"


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


MEDIAN_CHROMOSOMES_CREATE_STATEMENT = \
    """
    CREATE TABLE IF NOT EXISTS `median_chromosomes` (
        `generation_id` int NOT NULL,
        `chromosome_id` int NOT NULL,
        PRIMARY KEY (generation_id, chromosome_id),
        CONSTRAINT FOREIGN KEY (generation_id) REFERENCES genetic_algorithm(
        generation) ON DELETE CASCADE ON UPDATE CASCADE,
        CONSTRAINT FOREIGN KEY (chromosome_id) REFERENCES chromosomes(id)
        ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB;
    """


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
      `text_amount` double NOT NULL,
      `top_base_clusters_amount` int(11) NOT NULL,
      `min_term_occurrence_collection` int(11) NOT NULL,
      `max_term_ratio_collection` int(11) NOT NULL,
      `min_limit_base_cluster_score` int(11) NOT NULL,
      `max_limit_base_cluster_score` int(11) NOT NULL,
      `similarity_measure_method` int(11) NOT NULL,
      `similarity_measure_threshold` double NOT NULL,
      `similarity_measure_avg_cf_threshold` int(11) NOT NULL,
      `similarity_measure_cf_intersect_min` int(11) NOT NULL,
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
        `tag_accuracy_avg_0` double NOT NULL,
        `tag_accuracy_avg_1` double NOT NULL,
        `tag_accuracy_avg_2` double NOT NULL,
        `tag_accuracy_avg_3` double NOT NULL,
        `tag_accuracy_avg_4` double NOT NULL,
        `tag_accuracy_avg_5` double NOT NULL,
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
        `text_amount` double NOT NULL,
        `top_base_clusters_amount` int(11) NOT NULL,
        `min_term_occurrence_collection` int(11) NOT NULL,
        `max_term_ratio_collection` int(11) NOT NULL,
        `min_limit_base_cluster_score` int(11) NOT NULL,
        `max_limit_base_cluster_score` int(11) NOT NULL,
        `similarity_measure_method` int(11) NOT NULL,
        `similarity_measure_threshold` double NOT NULL,
        `similarity_measure_avg_cf_threshold` int(11) NOT NULL,
        `similarity_measure_cf_intersect_min` int(11) NOT NULL,
        `drop_singleton_base_clusters` tinyint(1) NOT NULL,
        `drop_one_word_clusters` tinyint(1) NOT NULL,
        `fitness` double NOT NULL,
        `fmeasure` double NOT NULL,
        `precision` double NOT NULL,
        `recall` double NOT NULL,
        `time` int NOT NULL,
        `number_of_clusters` int NOT NULL,
        `number_of_base_clusters` int NOT NULL,
        `tag_accuracy_0` double NOT NULL,
        `tag_accuracy_1` double NOT NULL,
        `tag_accuracy_2` double NOT NULL,
        `tag_accuracy_3` double NOT NULL,
        `tag_accuracy_4` double NOT NULL,
        `tag_accuracy_5` double NOT NULL,
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

INSERT_INTO_SAVED_POPULATION = "INSERT INTO saved_population (" \
                               "`id`, " \
                               "`tree_type_1`, " \
                               "`tree_type_2`, " \
                               "`tree_type_3`, " \
                               "`text_type_frontpageheading`, " \
                               "`text_type_frontpageintroduction`, " \
                               "`text_type_articleheading`, " \
                               "`text_type_articlebyline`, " \
                               "`text_type_articleintroduction`, " \
                               "`text_type_articletext`, " \
                               "`text_amount`, " \
                               "`top_base_clusters_amount`, " \
                               "`min_term_occurrence_collection`, " \
                               "`max_term_ratio_collection`, " \
                               "`min_limit_base_cluster_score`, " \
                               "`max_limit_base_cluster_score`, " \
                               "`similarity_measure_method`, " \
                               "`similarity_measure_threshold`, " \
                               "`similarity_measure_avg_cf_threshold`, " \
                               "`similarity_measure_cf_intersect_min`, " \
                               "`drop_singleton_base_clusters`, " \
                               "`drop_one_word_clusters`, " \
                               "`fitness`" \
                               ") VALUES ( " \
                               "%(id)s, " \
                               "%(tree_type_1)s, " \
                               "%(tree_type_2)s, " \
                               "%(tree_type_3)s, " \
                               "%(text_type_frontpageheading)s, " \
                               "%(text_type_frontpageintroduction)s, " \
                               "%(text_type_articleheading)s, " \
                               "%(text_type_articlebyline)s, " \
                               "%(text_type_articleintroduction)s, " \
                               "%(text_type_articletext)s, " \
                               "%(text_amount)s, " \
                               "%(top_base_clusters_amount)s, " \
                               "%(min_term_occurrence_collection)s, " \
                               "%(max_term_ratio_collection)s, " \
                               "%(min_limit_base_cluster_score)s, " \
                               "%(max_limit_base_cluster_score)s, " \
                               "%(similarity_measure_method)s, " \
                               "%(similarity_measure_threshold)s, " \
                               "%(similarity_measure_avg_cf_threshold)s, " \
                               "%(similarity_measure_cf_intersect_min)s, " \
                               "%(drop_singleton_base_clusters)s, " \
                               "%(drop_one_word_clusters)s, " \
                               "%(fitness)s )"

INSERT_INTO_CHROMOSOMES = "INSERT INTO chromosomes (" \
                          "`id`, " \
                          "`tree_type_1`, " \
                          "`tree_type_2`, " \
                          "`tree_type_3`, " \
                          "`text_type_frontpageheading`, " \
                          "`text_type_frontpageintroduction`, " \
                          "`text_type_articleheading`, " \
                          "`text_type_articlebyline`, " \
                          "`text_type_articleintroduction`, " \
                          "`text_type_articletext`, " \
                          "`text_amount`, " \
                          "`top_base_clusters_amount`, " \
                          "`min_term_occurrence_collection`, " \
                          "`max_term_ratio_collection`, " \
                          "`min_limit_base_cluster_score`, " \
                          "`max_limit_base_cluster_score`, " \
                          "`similarity_measure_method`, " \
                          "`similarity_measure_threshold`, " \
                          "`similarity_measure_avg_cf_threshold`, " \
                          "`similarity_measure_cf_intersect_min`, " \
                          "`drop_singleton_base_clusters`, " \
                          "`drop_one_word_clusters`, " \
                          "`fitness`, " \
                          "`time`, " \
                          "`number_of_clusters`, " \
                          "`number_of_base_clusters`, " \
                          "`precision`, " \
                          "`recall`, " \
                          "`fmeasure`, " \
                          "`tag_accuracy_0`, " \
                          "`tag_accuracy_1`, " \
                          "`tag_accuracy_2`, " \
                          "`tag_accuracy_3` ," \
                          "`tag_accuracy_4`, " \
                          "`tag_accuracy_5`, " \
                          "`precision_0`, " \
                          "`precision_1`, " \
                          "`precision_2`, " \
                          "`precision_3` ," \
                          "`precision_4`, " \
                          "`precision_5`, " \
                          "`recall_0`, " \
                          "`recall_1`, " \
                          "`recall_2`, " \
                          "`recall_3`, " \
                          "`recall_4`, " \
                          "`recall_5`, " \
                          "`f_measure_0`, " \
                          "`f_measure_1`, " \
                          "`f_measure_2`, " \
                          "`f_measure_3`, " \
                          "`f_measure_4`, " \
                          "`f_measure_5` " \
                          ") VALUES ( " \
                          "%(id)s, " \
                          "%(tree_type_1)s, " \
                          "%(tree_type_2)s, " \
                          "%(tree_type_3)s, " \
                          "%(text_type_frontpageheading)s, " \
                          "%(text_type_frontpageintroduction)s, " \
                          "%(text_type_articleheading)s, " \
                          "%(text_type_articlebyline)s, " \
                          "%(text_type_articleintroduction)s, " \
                          "%(text_type_articletext)s, " \
                          "%(text_amount)s, " \
                          "%(top_base_clusters_amount)s, " \
                          "%(min_term_occurrence_collection)s, " \
                          "%(max_term_ratio_collection)s, " \
                          "%(min_limit_base_cluster_score)s, " \
                          "%(max_limit_base_cluster_score)s, " \
                          "%(similarity_measure_method)s, " \
                          "%(similarity_measure_threshold)s, " \
                          "%(similarity_measure_avg_cf_threshold)s, " \
                          "%(similarity_measure_cf_intersect_min)s, " \
                          "%(drop_singleton_base_clusters)s, " \
                          "%(drop_one_word_clusters)s, " \
                          "%(fitness)s, " \
                          "%(time)s, " \
                          "%(number_of_clusters)s, " \
                          "%(number_of_base_clusters)s, " \
                          "%(precision)s, " \
                          "%(recall)s, " \
                          "%(fmeasure)s, " \
                          "%(tag_accuracy_0)s, " \
                          "%(tag_accuracy_1)s, " \
                          "%(tag_accuracy_2)s, " \
                          "%(tag_accuracy_3)s ," \
                          "%(tag_accuracy_4)s, " \
                          "%(tag_accuracy_5)s, " \
                          "%(precision_0)s, " \
                          "%(precision_1)s, " \
                          "%(precision_2)s, " \
                          "%(precision_3)s ," \
                          "%(precision_4)s, " \
                          "%(precision_5)s, " \
                          "%(recall_0)s, " \
                          "%(recall_1)s, " \
                          "%(recall_2)s, " \
                          "%(recall_3)s, " \
                          "%(recall_4)s, " \
                          "%(recall_5)s, " \
                          "%(f_measure_0)s, " \
                          "%(f_measure_1)s, " \
                          "%(f_measure_2)s, " \
                          "%(f_measure_3)s, " \
                          "%(f_measure_4)s, " \
                          "%(f_measure_5)s " \
                          ") ON DUPLICATE KEY UPDATE id=id"

INSERT_INTO_GENETIC_ALGORITHM = \
    """
    INSERT INTO genetic_algorithm
        (
            `generation`,
            `fitness_avg`,
            `fmeasure_avg`,
            `precision_avg`,
            `recall_avg`,
            `time_avg`,
            `number_of_clusters_avg`,
            `number_of_base_clusters_avg`,
            `tag_accuracy_avg_0`,
            `tag_accuracy_avg_1`,
            `tag_accuracy_avg_2`,
            `tag_accuracy_avg_3`,
            `tag_accuracy_avg_4`,
            `tag_accuracy_avg_5`,
            `precision_avg_0`,
            `precision_avg_1`,
            `precision_avg_2`,
            `precision_avg_3`,
            `precision_avg_4`,
            `precision_avg_5`,
            `recall_avg_0`,
            `recall_avg_1`,
            `recall_avg_2`,
            `recall_avg_3`,
            `recall_avg_4`,
            `recall_avg_5`,
            `fmeasure_avg_0`,
            `fmeasure_avg_1`,
            `fmeasure_avg_2`,
            `fmeasure_avg_3`,
            `fmeasure_avg_4`,
            `fmeasure_avg_5`
    )
    VALUES
        (
            %(generation)s,
            %(fitness_avg)s,
            %(fmeasure_avg)s,
            %(precision_avg)s,
            %(recall_avg)s,
            %(time_avg)s,
            %(number_of_clusters_avg)s,
            %(number_of_base_clusters_avg)s,
            %(tag_accuracy_avg_0)s,
            %(tag_accuracy_avg_1)s,
            %(tag_accuracy_avg_2)s,
            %(tag_accuracy_avg_3)s,
            %(tag_accuracy_avg_4)s,
            %(tag_accuracy_avg_5)s,
            %(precision_avg_0)s,
            %(precision_avg_1)s,
            %(precision_avg_2)s,
            %(precision_avg_3)s,
            %(precision_avg_4)s,
            %(precision_avg_5)s,
            %(recall_avg_0)s,
            %(recall_avg_1)s,
            %(recall_avg_2)s,
            %(recall_avg_3)s,
            %(recall_avg_4)s,
            %(recall_avg_5)s,
            %(fmeasure_avg_0)s,
            %(fmeasure_avg_1)s,
            %(fmeasure_avg_2)s,
            %(fmeasure_avg_3)s,
            %(fmeasure_avg_4)s,
            %(fmeasure_avg_5)s
        )
    """

INSERT_INTO_BEST_CHROMOSOMES = \
    """
    INSERT INTO best_chromosomes (`generation_id`, `chromosome_id`)
    VALUES (%s, %s)
    """

INSERT_INTO_WORST_CHROMOSOMES = \
    """
    INSERT INTO worst_chromosomes (`generation_id`, `chromosome_id`)
    VALUES (%s, %s)
    """

INSERT_INTO_MEDIAN_CHROMOSOMES = \
    """
    INSERT INTO median_chromosomes
        (`generation_id`, `chromosome_id`)
    VALUES
        (%s, %s)
    """