import os
import yaml
import torch
import logging
from src.Pdf_annotation_pipeline.utils.pdf_image_engine import PDFImageEngine
from src.Pdf_annotation_pipeline.utils.custom_dataset_engine import CustomDatasetEngine
from src.Pdf_annotation_pipeline.utils.prepare_model_engine import PrepareModelEngine
from src.Pdf_annotation_pipeline.utils.extract_embeddings_engine import ExtractEmbeddingsEngine
from src.Pdf_annotation_pipeline.utils.get_cluster_engine import GetClusterEngine
from src.Pdf_annotation_pipeline.utils.train_kmeans_engine import TrainKmeansEngine
from src.Pdf_annotation_pipeline.utils.clustering_map_engine import ClusteringMapEngine
from src.Pdf_annotation_pipeline.utils.reduce_dimension_engine import ReduceDimensionEngine
from src.Pdf_annotation_pipeline.utils.dataframe_engine import DataFrameEngine
from src.Pdf_annotation_pipeline.utils.determine_each_pdf_group import DetermineEachPdfGroup
from src.Post_Processing_Folder.Post_Processing_to_PubLayNet_format.publyanet_mapping_engine import PublaynetMappingEngine

class PDFAnnotationPipeline:
    """
    This class is the pipeline for the PDF annotation process. It is responsible for orchestrating the different engines
    that are used in the process. The engines are responsible for the different steps in the process.
    Check the documentation of each engine to understand what each engine does available in https://github.com/ICA-PUC/Synthetic_document_pipeline.

    The pipeline is responsible for the following steps:
    1. Extract images from PDFs
    2. Prepare the dataset for the deep learning model in use 
    3. Extract embeddings from the model
    4. Manage the embeddings
    5. Get the clusters
    6. Train the KMeans model
    7. Map the clusters
    8. Reduce the dimension of the embeddings
    9. Create a dataframe with the results
    10. Determine each PDF group

    Remember to check the documentation of each engine to understand what each engine does.

    Attributes:
        config_path (str): A string containing the path to the configuration file.

    Methods:
        - load_config: This method loads the configuration file.
        choose_pdf_per_group: This method is responsible for orchestrating the different engines that are used in the process.
        - At the end of the process, the user will have different folders with the PDFs grouped by the clusters.
        - convert_annotations_to_publyanet_format: This function is responsible for converting the annotations from the VoTT tool to the PubLayNet format.
    """
    def __init__(self, config_path: str, setup_logger: callable):
        """
        The constructor of the PDFAnnotationPipeline class.
        """
        self.config_path = config_path
        self.config = self.load_config()        
        self.setup_logger = setup_logger
        process_output_path = self.config["Pdf_selector"]["Parameters"]["process_output_path"]
        logger_file = os.path.join(process_output_path, f'Pdf_selector_logs.log')
        if os.path.isfile(logger_file):
            os.remove(logger_file)
        self.logger = self.setup_logger(name='Pdf_selector', log_file=logger_file, level=logging.INFO)

    def load_config(self):
        """
        This method loads the configuration file.
        """
        with open(self.config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        return self.config
    
    def choose_pdf_per_group(self):
        """
        This function is responsible for orchestrating the different engines that are used in the process.
        At the end of the process, the user will have different folders with the PDFs grouped by the clusters.

        Returns:
        --------
            None. However, the user will have different folders with the PDFs grouped by the clusters.
        """

        if self.config["Pdf_selector"]["should_perform"]:
            self.process_output_path = self.config["Pdf_selector"]["Parameters"]["process_output_path"]
            self.pdfs_folder = self.config["Pdf_selector"]['Parameters']['documents_Pdf_path']
            self.desired_folder_name = self.config["Pdf_selector"]['Parameters']['desired_folder_name']
            self.desired_image_format = self.config["Pdf_selector"]['Parameters']['desired_image_format']
            self.shape_resize = tuple(map(int, self.config["Pdf_selector"]['Parameters']['image_resize_size']))
            self.is_fine_tuned_model = self.config["Pdf_selector"]['Parameters']['is_fine_tuned_model']
            self.path_to_fine_tuned_model = self.config["Pdf_selector"]['Parameters']['path_to_fine_tuned_model']
            self.path_to_download_model = self.config["Pdf_selector"]['Parameters']['path_to_download_model']
            self.desired_model_folder_name = self.config["Pdf_selector"]['Parameters']['desired_model_folder_name']
            self.model_name = self.config["Pdf_selector"]['Parameters']['deep_learning_model_name']
            self.model_weights = self.config["Pdf_selector"]['Parameters']['deep_learning_model_weights']
            self.batch_size = self.config["Pdf_selector"]['Parameters']['batch_size']
            self.num_channels = self.config["Pdf_selector"]['Parameters']['num_channels']
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.shuffle_dataloader = self.config["Pdf_selector"]['Parameters']['should_shuffle_dataset']
            self.save_embedding_extracted = self.config["Pdf_selector"]['Parameters']['should_save_embedding_extracted']
            self.desired_clusters_list = tuple(map(int, self.config["Pdf_selector"]['Parameters']['desired_cluster_list']))
            self.which_cluster_method = self.config["Pdf_selector"]['Parameters']['clustering_method']
            self.n_init = self.config["Pdf_selector"]['Parameters']['n_init']
            self.reduction_method = self.config["Pdf_selector"]['Parameters']['reduction_method']
            self.random_state = self.config["Pdf_selector"]['Parameters']['random_state']
            self.desired_perplexity_range = tuple(map(int, self.config["Pdf_selector"]['Parameters']['desired_perplexity_range_for_tsne']))
            self.n_components = self.config["Pdf_selector"]['Parameters']['how_many_components']
            self.t_SNE_init = self.config["Pdf_selector"]['Parameters']['t_SNE_initializer']
            self.should_save_best_embeddings = self.config["Pdf_selector"]['Parameters']['should_save_best_embedding']
            self.desired_columns_names = self.config["Pdf_selector"]['Parameters']['desired_dataframe_columns_name']
            self.save_dataframe_to_excel = self.config["Pdf_selector"]['Parameters']['should_convert_dataframe_to_excel']
            self.logger.info(f"Starting the PDF selector process from the configuration file {self.config_path} and by setting the flag should_perform to True in the configuration.")

            pdf_convertor = PDFImageEngine(pdfs_folder_path=self.pdfs_folder,
                                        path_to_save_image=self.process_output_path,
                                        desired_folder_name = self.desired_folder_name,
                                        image_format=self.desired_image_format)
            self.logger.info(f'Starting the PDFs conversion to images process !')
            total_pdfs, image_list=pdf_convertor.convert_pdf_to_image()
            #pdfs_metadata = pdf_convertor.get_pdfs_metadata()
            self.logger.info(f"{total_pdfs} PDF documents were successfully converted into {len(image_list)} images and their metadata successfully extracted !")

            custom_dataset = CustomDatasetEngine(image_list=image_list, shape_resize=self.shape_resize)
            model = PrepareModelEngine()
            if self.is_fine_tuned_model:
                self.logger.info(f"Fine-tuned {self.model_name} model is being prepared !")
                model_without_last_layer, get_model_summary = model.use_fine_tuned_model(model_name=self.model_name,
                                        model_weights_path=self.path_to_fine_tuned_model,
                                        shape_resize=self.shape_resize,
                                        batch_size=self.batch_size,
                                        num_channels=self.num_channels,
                                        device=self.device,
                                        display_model_summary=True)
                self.logger.info(f"Fine-tuned {self.model_name} model prepared successfully !")
                #self.logger.info(f"The model summary is as follows:\n{get_model_summary}")
            else:
                self.logger.info(f"Model {self.model_name} is being prepared !")
                model_without_last_layer, get_model_summary = model.prepare_model(path_to_download_model=self.path_to_download_model,
                                                            desired_folder_name=self.desired_model_folder_name,
                                                            model_name=self.model_name,
                                                            model_weights=self.model_weights,
                                                            shape_resize=self.shape_resize,
                                                            batch_size=self.batch_size,
                                                            num_channels=self.num_channels,
                                                            device=self.device,
                                                            display_model_summary=True)
                self.logger.info(f"Model {self.model_name} prepared successfully !")
                #self.logger.info(f"The model summary is as follows:\n{get_model_summary}")

            embeddings_extractor = ExtractEmbeddingsEngine(dataset=custom_dataset,
                                                        model=model_without_last_layer,
                                                        batch_size=self.batch_size,
                                                        shuffle_dataloader=self.shuffle_dataloader,
                                                        save_embedding_extracted=self.save_embedding_extracted,
                                                        device=self.device,
                                                        path_to_save_embeddings=self.process_output_path)
            self.logger.info(f"Extracting embeddings from the model {self.model_name} !")
            embeddings_extracted = embeddings_extractor.extract_embeddings()
            self.logger.info(f"Embeddings extracted successfully !")

            get_cluster = GetClusterEngine(desired_clusters_list=self.desired_clusters_list,
                                        embeddings_extracted=embeddings_extracted,
                                        which_cluster_method=self.which_cluster_method,
                                        n_init=self.n_init,
                                        random_state=self.random_state,
                                        path_to_save_graph=self.process_output_path)
            self.logger.info(f"Getting the best cluster using the {self.which_cluster_method} method !")
            best_cluster = get_cluster.get_best_clusters()
            self.logger.info(f"Best cluster found successfully after using the {self.which_cluster_method} method ! The best cluster is {best_cluster}.")
            
            train_kmeans = TrainKmeansEngine(embeddings_extracted=embeddings_extracted,
                                            best_cluster=best_cluster,
                                            n_init=self.n_init,
                                            random_state=self.random_state)
            self.logger.info(f"Training the KMeans model with the best cluster found !")
            kmeans_prediction = train_kmeans.get_predicted_clusters()
            self.logger.info(f"KMeans model trained successfully and predicted clusters were obtained !")

            reduce_dimension = ReduceDimensionEngine()
            if self.reduction_method == 'tsne':
                self.logger.info(f"Reducing the dimension of the embeddings with the {self.reduction_method} algorithm !")
                best_embedding_reduced = reduce_dimension.reduce_dimension_with_tSNE(desired_perplexity_range=self.desired_perplexity_range,
                                                        n_components=self.n_components,
                                                        embeddings_extracted=embeddings_extracted,
                                                        t_SNE_init=self.t_SNE_init,
                                                        random_state=self.random_state,
                                                        path_to_save_div_vs_perp=self.process_output_path,
                                                        should_save_best_embeddings=self.should_save_best_embeddings,
                                                        path_to_save_best_embeddings=self.process_output_path)
                self.logger.info(f"Embeddings dimension reduced successfully with the {self.reduction_method} algorithm !")
            elif self.reduction_method == 'pca':
                #To do
                pass
            elif self.reduction_method == 'lda':
                #To do
                pass
            elif self.reduction_method == 'mds':
                #To do
                pass
            elif self.reduction_method == 'isomap':
                #To do
                pass
            elif self.reduction_method == 'umap':
                #To do
                pass
            elif self.reduction_method == 'ded': # Deep Embedding Clustering Driven by Sample Stability: https://arxiv.org/abs/2401.15989
                #To do
                pass
            else:
                raise ValueError(f"The reduction method {self.reduction_method} is not supported. It should be one of the following: tsne, pca, lda, mds, isomap, umap, ded. Check it out !")

            dataframe = DataFrameEngine()
            self.logger.info(f"Creating the dataframe with the results !")
            created_dataframe = dataframe.create_dataframe(best_reduced_embeddings=best_embedding_reduced,
                                                        kmeans_prediction=kmeans_prediction,
                                                        desired_columns_names=self.desired_columns_names,
                                                        embeddings_extracted=embeddings_extracted, 
                                                        save_to_excel_format=self.save_dataframe_to_excel,
                                                        path_to_save_dataframe=self.process_output_path)
            self.logger.info(f"Dataframe created successfully !")

            clustering_map = ClusteringMapEngine()
            self.logger.info(f"Creating the cluster map !")
            clustering_map.visualize_clusters(best_embeddings_df=created_dataframe, 
                                              path_to_save_cluster_map=self.process_output_path)
            self.logger.info(f"Cluster map created successfully and saved at {self.process_output_path} !")

            determine_pdf_group = DetermineEachPdfGroup()
            self.logger.info(f"Determining images per group !")
            meta_data_folder=determine_pdf_group.fill_folder_with_images(best_cluster=best_cluster,
                                                                        path_to_save_pdf_per_group=self.process_output_path,
                                                                        dataframe=created_dataframe,
                                                                        image_path_list=image_list)

            self.logger.info(f"Images filled in the folder successfully !")
            self.logger.info(f"Using the cosine similarity check to select the PDFs images to annotate !")
            dataframe.cosine_similarity_check(embeddings_extracted=embeddings_extracted,
                                              Kmeans_prediction=kmeans_prediction,
                                              meta_data_folder=meta_data_folder,
                                              path_to_save_folders=self.process_output_path)
    
            self.logger.info(f"PDFs images selected successfully think to the cosine similarity check !")

        else:
            self.logger.warn(f"Dear user you has chosen not to perform the PDF selector step by setting the should_perform parameter in the configuration file to False.\n"
                        f"This means that you has already performed the PDF selector step and annotated the PDFs. Check it out !")
    
    def convert_annotations_to_publyanet_format(self):
        
        """
        This convert a given annotation file from the VoTT tool to the PubLayNet format.
        """
        if self.config["Post_processor_to_publaynet"]["should_perform"]:
            self.vott_json_path = self.config["Post_processor_to_publaynet"]["Parameters"]["path_to_the_vott_file"]
            self.image_meta_id = self.config["Post_processor_to_publaynet"]["Parameters"]["image_id_starter"]
            self.annotation_id_start = self.config["Post_processor_to_publaynet"]["Parameters"]["annotation_id_starter"]
            self.path_to_save = self.config["Post_processor_to_publaynet"]["Parameters"]["path_to_save_publyanet_format"]
            self.desired_name = self.config["Post_processor_to_publaynet"]["Parameters"]["desired_name"]
            
            PubLayNet_format = PublaynetMappingEngine(vott_json_path=self.vott_json_path,
                                                        image_meta_id=self.image_meta_id,
                                                        annotation_id_start=self.annotation_id_start,
                                                        path_to_save=self.path_to_save,
                                                        desired_name=self.desired_name)
            self.logger.info(f"Starting the process to convert the annotations from the VoTT format to the PubLayNet format !")
            PubLayNet_format.map_vott_to_publaynet()
            self.logger.info(f"Annotations converted successfully to the PubLayNet format and saved in the folder {self.path_to_save} under the name {self.desired_name}_publyanet.json !")
        else:
            self.logger.warn(f"Dear user you has chosen not to perform the Post processor to PubLayNet format step by setting the should_perform parameter in the configuration file to False.\n"
                        f"This means that you has already performed the Post processor to PubLayNet format step or not. Check it out !")