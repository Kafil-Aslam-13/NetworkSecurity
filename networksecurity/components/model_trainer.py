import os,sys
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact
from networksecurity.entity.config_entity import ModelTrainerConfig

from networksecurity.utils.main_utils.utils import save_object,load_object
from networksecurity.utils.main_utils.utils import load_numpy_array_data,evaluate_models
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
import mlflow


from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier
)



class ModelTrainer:
    def __init__(self,model_trainer_config:ModelTrainerConfig,data_transformation_artifact:DataTransformationArtifact):
        try:
            self.model_trainer_config=model_trainer_config
            self.data_transformation_artifact=data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        pass

    def track_mlflow(self,best_model,classification_metric):
        with mlflow.start_run():
            f1_score=classification_metric.f1_score
            precision_score=classification_metric.presition_score
            recall_score=classification_metric.recall_score

            mlflow.log_metrics("f1_score",f1_score)
            mlflow.log_metrics("precision_score",precision_score)
            mlflow.log_metrics("recall_score",recall_score)
            mlflow.sklearn.log_model(best_model,"model")







 ## here in train model we will perform both taining and evaluation of models
    def train_model(self,x_train,y_train,x_test,y_test):
        ## iniotialize all my models
        models={
            "Random Forest": RandomForestClassifier(verbose=1),
            "Decision Tree": DecisionTreeClassifier(),
            "Gradient Boosting":GradientBoostingClassifier(verbose=1),
            "Logistic Regression":LogisticRegression(verbose=1),
            "AdaBoost": AdaBoostClassifier(),
        }
        params={
            "Decision Tree":{
                'criterion':['gini','entropy','logloss'],
                # 'splitter':['best','random'],
                # 'max_features':['sqrt','log2'],
            },
            "Random Forest":{
                # 'criterion':['gini','entropy','logloss'],
                # 'max_features':['sqrt','log2','None'],
                'n_estimators':[8,16,32,64,128,256]
            },
            "Gradient Boosting":{
                # 'loss':['log_loss','exponential'],
                'learning_rate':[.1,.01,.05,.001],
                'subsample':[0.6,0.7,0.75,0.8,0.85,0.9],
                # 'criterion':['squared_error','friedman_mse'],
                # 'max_features':['sqrt','log2','auto'],
                'n_estimators':[8,16,32,64,128,256]
            },
            "Logistic Regression":{},
            "AdaBoost":{
                'learning_rate':[.1,.01,.05,.001],
                'n_estimators':[8,16,32,64,128,256]
                
            }
        }

        model_report:dict=evaluate_models(X_train=x_train,y_train=y_train,X_test=x_test,y_test=y_test,models=models,param=params)
        best_model_score=max(sorted(model_report.values()))
        best_model_name=list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]
        best_model=models[best_model_name]
        y_train_pred=best_model.predict(x_train)
        classification_train_metric=get_classification_score(y_true=y_train,y_pred=y_train_pred)
        ## we will do tracking of experiments with mlflow later here below
        ## mlflow is amazing bcz here we will be able to see entire logs in  mlflows ui , what performance might be getting captured and which ias ur model file etc
        self.track_mlflow(best_model,classification_train_metric)

        y_test_pred=best_model.predict(x_test)
        classification_test_metric=get_classification_score(y_true=y_test,y_pred=y_test_pred)

        self.track_mlflow(best_model,classification_test_metric)


        preprocessor=load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
        model_dir_path=os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path,exist_ok=True)

        Network_Model=NetworkModel(preprocessor=preprocessor,model=best_model)
        save_object(self.model_trainer_config.trained_model_file_path,obj=Network_Model)


        ## Model trainer artifact
        model_trainer_artifact=ModelTrainerArtifact(trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                             train_metric_artifact=classification_train_metric,
                             test_metric_artifact=classification_test_metric)
        return model_trainer_artifact



    def initiate_model_trainer(self)->ModelTrainerArtifact:
        try:
            train_file_path=self.data_transformation_artifact.transformed_train_file_path
            test_file_path=self.data_transformation_artifact.transformed_test_file_path

             ##loading training and test file paths
            train_arr=load_numpy_array_data(train_file_path)
            test_arr=load_numpy_array_data(test_file_path)

            x_train,y_train,x_test,y_test=(
                train_arr[:,:-1],
                train_arr[:,-1],
                test_arr[:,:-1],
                test_arr[:,-1]
            )
            model_trainer_artifact=self.train_model(x_train,y_train,x_test,y_test)
            return model_trainer_artifact


        except Exception as e:
            raise NetworkSecurityException(e,sys)




