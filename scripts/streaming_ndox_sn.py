import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

SALT = os.environ.get('NDOX_SECRET_SALT', 'default_salt')

spark = SparkSession.builder \
    .appName('Ndocx_SN_Streaming') \
    .config('spark.sql.shuffle.partitions', '4') \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2") \
    .config("spark.network.maxRemoteBlockSizeFetchToMem", "1g") \
    .config("spark.rpc.message.maxSize", "1024") \
    .config("spark.sql.adaptive.enabled", "false") \
    .getOrCreate()

spark.sparkContext.setLogLevel('WARN')

press_schema = StructType([
    StructField('capteur_id', StringType(), True),
    StructField('zone', StringType(), True),
    StructField('pression_bars', FloatType(), True),
    StructField('pression_nominale', FloatType(), True),
    StructField('debit_m3h', FloatType(), True),
    StructField('statut_capteur', StringType(), True),
    StructField('age_canalisation_ans', FloatType(), True),
    StructField('timestamp', StringType(), True)
])

raw_df = (spark.readStream
          .format('kafka')
          .option('kafka.bootstrap.servers', 'localhost:9092')
          .option('subscribe', 'ndox_pression_raw')
          .option('startingOffsets', 'earliest')
          .option('maxOffsetsPerTrigger', 100)
          .option('kafka.session.timeout.ms', '60000')
          .option('kafka.request.timeout.ms', '61000')
          .option('kafka.fetch.max.wait.ms', '5000')
          .option('failOnDataLoss', 'false')
          .load()
          .select(from_json(col('value').cast('string'), press_schema).alias('data'))
          .select('data.*')
          .withColumn('event_ts', current_timestamp())
)

criticity_df = raw_df.withColumn(
    'ratio_pression',
    when(col('pression_nominale') > 0,
         col('pression_bars') / col('pression_nominale')
    ).otherwise(0.0)
).withColumn(
    'criticite',
    when(col('ratio_pression') < 0.3, lit('CRITIQUE'))
    .when(col('ratio_pression') < 0.6, lit('ALERTE'))
    .when(col('ratio_pression') < 0.8, lit('SURVEILLANCE'))
    .otherwise(lit('NORMAL'))
).withColumn('capteur_anonymise',
    sha2(concat(lit(SALT), col('capteur_id')), 256)
)

enriched_df = criticity_df.withColumn(
    'score_priorite',
    (when(col('pression_nominale') > 0,
          (col('pression_nominale') - col('pression_bars')) / col('pression_nominale')
         ).otherwise(0.0) * 0.4)
    + when(col('debit_m3h') < 250, 0.3).otherwise(0.0)
    + (col('age_canalisation_ans') / 100.0) * 0.2
    + when(~lower(col('statut_capteur')).isin(['normal', 'ok', '']), 0.1).otherwise(0.0)
).withColumn('score_priorite', round(col('score_priorite'), 3))

query = (enriched_df.writeStream
         .outputMode('append')
         .format('parquet')
         .option('path', '/home/omar/ndox-sn/data/maintenance_prioritaire')
         .option('checkpointLocation', '/home/omar/ndox-sn/checkpoint')
         .partitionBy('zone')
         .trigger(processingTime='30 seconds')
         .start()
)

print("Streaming Spark démarré. Topic: ndox_pression_raw -> Parquet partitionné par zone")
query.awaitTermination()