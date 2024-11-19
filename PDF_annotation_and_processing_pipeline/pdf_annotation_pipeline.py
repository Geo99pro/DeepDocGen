import os
import yaml
import torch
import warnings
import logging
from PDF_annotation_and_processing_pipeline.utils.pdf_image_engine import PDFImageEngine
from PDF_annotation_and_processing_pipeline.utils.custom_dataset_engine import CustomDatasetEngine
from PDF_annotation_and_processing_pipeline.utils.prepare_model_engine import PrepareModelEngine
from PDF_annotation_and_processing_pipeline.utils.extract_embeddings_engine import ExtractEmbeddingsEngine
from PDF_annotation_and_processing_pipeline.utils.get_cluster_engine import GetClusterEngine
from PDF_annotation_and_processing_pipeline.utils.train_kmeans_engine import TrainKmeansEngine
from PDF_annotation_and_processing_pipeline.utils.clustering_map_engine import ClusteringMapEngine
from PDF_annotation_and_processing_pipeline.utils.reduce_dimension_engine import ReduceDimensionEngine
from PDF_annotation_and_processing_pipeline.utils.dataframe_engine import DataFrameEngine
from PDF_annotation_and_processing_pipeline.utils.determine_each_pdf_group import DetermineEachPdfGroup
from Post_Processing_Folder.Post_Processing_to_PubLayNet_format.publyanet_mapping_engine import PublaynetMappingEngine

class PDFAnnotationPipeline:
    """
    This class is the pipeline for the PDF annotation process. It is responsible for orchestrating the different engines
    that are used in the process. The engines are responsible for the different steps in the process.
    Check the documentation of each engine to understand what each engine does available in https://github.com/ICA-PUC/Synthetic_document_pipeline.

    The pipeline is responsible for the following steps:
    1. Extract images from PDFs
    2. Prepare the dataset for the model ResNet-152
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
    def __init__(self, config_path: str):
        """
        The constructor of the PDFAnnotationPipeline class.
        """
        self.config_path = config_path
        self.config = self.load_config()
            
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
            self.pdf_folder = self.config["Pdf_selector"]['Parameters']['documents_Pdf_path']
            self.save_image_path = self.config["Pdf_selector"]['Parameters']['where_to_save_conversion_pdf_to_image']
            self.desired_image_format = self.config["Pdf_selector"]['Parameters']['desired_image_format']
            self.shape_resize = tuple(map(int, self.config["Pdf_selector"]['Parameters']['resize_image_for_extractor_model']))
            self.path_to_download_model = self.config["Pdf_selector"]['Parameters']['where_to_download_model']
            self.model_name = self.config["Pdf_selector"]['Parameters']['deep_learning_model_name']
            self.model_weights = self.config["Pdf_selector"]['Parameters']['deep_learning_model_weights']
            self.batch_size = self.config["Pdf_selector"]['Parameters']['inference_batch_size']
            self.num_channels = self.config["Pdf_selector"]['Parameters']['expected_model_channel_number']
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.shuffle_dataloader = self.config["Pdf_selector"]['Parameters']['should_shuffle_dataset']
            self.save_embedding_extracted = self.config["Pdf_selector"]['Parameters']['should_save_embedding_extracted']
            self.path_to_save_embeddings = self.config["Pdf_selector"]['Parameters']['where_to_save_embedding']
            self.desired_clusters_list = tuple(map(int, self.config["Pdf_selector"]['Parameters']['desired_cluster_list']))
            self.which_cluster_method = self.config["Pdf_selector"]['Parameters']['which_clustering_method']
            self.n_init = self.config["Pdf_selector"]['Parameters']['n_init']
            self.random_state = self.config["Pdf_selector"]['Parameters']['random_state']
            self.path_to_save_graph = self.config["Pdf_selector"]['Parameters']['where_to_save_cluster_method_graph']
            self.desired_perplexity_range = tuple(map(int, self.config["Pdf_selector"]['Parameters']['desired_perplexity_range_for_tsne']))
            self.n_components = self.config["Pdf_selector"]['Parameters']['how_many_components']
            self.t_SNE_init = self.config["Pdf_selector"]['Parameters']['t_SNE_initializer']
            self.path_to_save_div_vs_perp = self.config["Pdf_selector"]['Parameters']['where_to_save_tSNE_div_vs_perp_graph']
            self.path_to_save_cluster_map = self.config["Pdf_selector"]['Parameters']['where_to_save_cluster_map_image']
            self.should_save_best_embeddings = self.config["Pdf_selector"]['Parameters']['should_save_best_embedding']
            self.desired_columns_names = self.config["Pdf_selector"]['Parameters']['desired_dataframe_columns_name']
            self.save_dataframe_to_excel = self.config["Pdf_selector"]['Parameters']['should_convert_dataframe_to_excel']
            self.path_to_save_excel = self.config["Pdf_selector"]['Parameters']["where_to_save_excel"]
            self.path_to_save_pdf_per_group = self.config["Pdf_selector"]['Parameters']['where_to_save_pdfs_per_group']
            logger_file = os.path.join(self.config["Pdf_selector"]['Parameters']['where_to_save_log_file'], f'Pdf_selector_logs.log')
            logging.basicConfig(filename=logger_file, level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', filemode='w')
            logging.info(f"Starting the PDF selector process by setting the flag should_perform to True in the configuration.")
            logging.info(f"Starting the PDF selector process from the configuration file {self.config_path}...")

            pdf_convertor = PDFImageEngine(pdf_folder_path=self.pdf_folder,
                                        save_image_path=self.save_image_path,
                                        desired_image_format=self.desired_image_format)
            image_list=pdf_convertor.convert_pdf_to_image()
            logging.info(f"PDFs converted to images successfully !")

            pdfs_metadata = pdf_convertor.get_pdfs_metadata()
            logging.info(f"PDFs metadata extracted successfully !")

            custom_dataset = CustomDatasetEngine(image_list=image_list, shape_resize=self.shape_resize)
            model = PrepareModelEngine(path_to_download_model=self.path_to_download_model,
                                        model_name=self.model_name,
                                        model_weights=self.model_weights,
                                        shape_resize=self.shape_resize,
                                        batch_size=self.batch_size,
                                        num_channels=self.num_channels,
                                        device=self.device)
            model_without_last_layer = model.prepare_model()
            logging.info(f"Model prepared successfully !")

            embeddings_extractor = ExtractEmbeddingsEngine(dataset=custom_dataset,
                                                        model=model_without_last_layer,
                                                        batch_size=self.batch_size,
                                                        shuffle_dataloader=self.shuffle_dataloader,
                                                        save_embedding_extracted=self.save_embedding_extracted,
                                                        device=self.device,
                                                        path_to_save_embeddings=self.path_to_save_embeddings)
            embeddings_extracted = embeddings_extractor.extract_embeddings()
            logging.info(f"Embeddings extracted successfully !")

            get_cluster = GetClusterEngine(desired_clusters_list=self.desired_clusters_list,
                                        embeddings_extracted=embeddings_extracted,
                                        which_cluster_method=self.which_cluster_method,
                                        n_init=self.n_init,
                                        random_state=self.random_state,
                                        path_to_save_graph=self.path_to_save_graph)
            best_cluster = get_cluster.get_best_clusters()
            logging.info(f"Best cluster found successfully after using the {self.which_cluster_method} method ! The best cluster is {best_cluster}.")
            
            train_kmeans = TrainKmeansEngine(embeddings_extracted=embeddings_extracted,
                                            best_cluster=best_cluster,
                                            n_init=self.n_init,
                                            random_state=self.random_state)
            kmeans_prediction = train_kmeans.get_predicted_clusters()
            logging.info(f"KMeans model trained successfully and predicted clusters were obtained !")

            reduce_dimension = ReduceDimensionEngine(desired_perplexity_range=self.desired_perplexity_range,
                                                    n_components=self.n_components,
                                                    embeddings_extracted=embeddings_extracted,
                                                    t_SNE_init=self.t_SNE_init,
                                                    random_state=self.random_state,
                                                    path_to_save_div_vs_perp=self.path_to_save_div_vs_perp,
                                                    should_save_best_embeddings=self.should_save_best_embeddings,
                                                    path_to_save_best_embeddings=self.path_to_save_embeddings)
            best_embedding_reduced = reduce_dimension.reduce_dimension_with_tSNE()
            logging.info(f"Dimension reduced successfully with t-SNE !")

            dataframe = DataFrameEngine(best_reduced_embeddings=best_embedding_reduced,
                                        kmeans_prediction=kmeans_prediction,
                                        desired_columns_names=self.desired_columns_names,
                                        embeddings_extracted=embeddings_extracted, 
                                        save_to_excel_format=self.save_dataframe_to_excel,
                                        path_to_save_dataframe=self.path_to_save_excel)
            created_dataframe = dataframe.create_dataframe()
            logging.info(f"Dataframe created successfully !")

            clustering_map = ClusteringMapEngine(best_embeddings_df=created_dataframe,
                                                path_to_save_cluster_map=self.path_to_save_cluster_map)
            clustering_map.visualize_clusters()
            logging.info(f"Cluster map created successfully and saved at {self.path_to_save_cluster_map} !")

            determine_pdf_group = DetermineEachPdfGroup(pdf_folder_path=self.pdf_folder,
                                                        dataframe=created_dataframe,
                                                        pdf_metadata=pdfs_metadata,
                                                        best_cluster=best_cluster,
                                                        path_to_save_pdf_per_group=self.path_to_save_pdf_per_group,
                                                        image_path_list=image_list)
            meta_data_folder=determine_pdf_group.fill_folder_with_images()
            logging.info(f"Images filled in the folder successfully !")
            dataframe.test_cosine_similarity(meta_data_folder=meta_data_folder)
    
            #pdf_group_meta= determine_pdf_group.determine_each_pdf_group()
            logging.info(f"PDFs images selected successfully for annotation !")

            #determine_pdf_group.find_pdf_per_group_and_fit_folder(pdf_group_meta=pdf_group_meta)
            #logging.info(f"PDF selector process completed successfully after grouping the PDFs !")
        else:
            warnings.warn(f"Dear user you has chosen not to perform the PDF selector step by setting the should_perform parameter in the configuration file to False.\n"
                        f"This means that you has already performed the PDF selector step and annotated the PDFs. Check it out !")
    
    def convert_annotations_to_publyanet_format(self):
        
        """
        This convert a given annotation file from the VoTT tool to the PubLayNet format.
        """

        if self.config["Post_processor_to_publaynet"]["should_perform"]:
            self.vott_json_path = self.config["Post_processor_to_publaynet"]["Parameters"]["where_is_the_Vott_json_file"]
            self.image_meta_id = self.config["Post_processor_to_publaynet"]["Parameters"]["image_id_starter"]
            self.annotation_id_start = self.config["Post_processor_to_publaynet"]["Parameters"]["annotation_id_starter"]
            self.path_to_save = self.config["Post_processor_to_publaynet"]["Parameters"]["where_to_save_publaynet_format"]
            self.desired_name = self.config["Post_processor_to_publaynet"]["Parameters"]["which_name_to_save"]
            
            PubLayNet_format = PublaynetMappingEngine(vott_json_path=self.vott_json_path,
                                                        image_meta_id=self.image_meta_id,
                                                        annotation_id_start=self.annotation_id_start,
                                                        path_to_save=self.path_to_save,
                                                        desired_name=self.desired_name)
            PubLayNet_format.map_vott_to_publaynet()
        else:
            warnings.warn(f"Dear user you has chosen not to perform the Post processor to PubLayNet format step by setting the should_perform parameter in the configuration file to False.\n"
                        f"This means that you has already performed the Post processor to PubLayNet format step or not. Check it out !")