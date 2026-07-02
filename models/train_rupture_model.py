from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import GBTClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
import mlflow
import mlflow.spark

spark = SparkSession.builder.appName("TrainRuptureModel") \
    .config("spark.sql.catalogImplementation", "hive") \
    .enableHiveSupport() \
    .getOrCreate()

# Lire depuis Hive Metastore qui écoute sur localhost:10000
df = spark.sql("SELECT ratio_pression_moy, age_moy_canalisation, nb_alertes_24h, "
               "CASE WHEN statut_zone='CRITIQUE' THEN 1 ELSE 0 END as label "
               "FROM ndox_sn.vue_etat_reseau")

assembler = VectorAssembler(inputCols=["ratio_pression_moy", "age_moy_canalisation", "nb_alertes_24h"],
                            outputCol="features")
data = assembler.transform(df).select("features", "label")
train, test = data.randomSplit([0.8, 0.2])

mlflow.set_experiment("ndox_rupture")
with mlflow.start_run():
    gbt = GBTClassifier(maxIter=50, maxDepth=5, seed=42)
    model = gbt.fit(train)
    pred = model.transform(test)
    evaluator = BinaryClassificationEvaluator(metricName="areaUnderROC")
    roc = evaluator.evaluate(pred)
    mlflow.log_metric("roc_auc", roc)
    mlflow.spark.log_model(model, "gbt_rupture_model")
    print(f"Modèle entraîné, AUC ROC = {roc:.3f}")