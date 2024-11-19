[//]: <> (https://stackoverflow.com/questions/47344571/how-to-draw-checkbox-or-tick-mark-in-github-markdown-table)
[//]: <> (https://docs.document360.com/docs/how-to-center-align-the-text-in-markdown)
<p align="center">
<a href="mailto: lhodonou349@gmail.com">
   <img alt="emal" src="https://img.shields.io/badge/contact_me-email-red">
</a>
</p>

# PDFs EMBEDDING EXTRACTOR AND CLUSTERING 🪑

PDFs Embedding Extractor and Clustering is a project aimed at automating the analysis, classification and organization of PDF documents on a large scale. The main objective is to extract vector representations (or embeddings) of PDF documents, enabling their semantic content to be captured in a way that can be understood by machine learning algorithms. These vector representations facilitate the application of clustering techniques, which group similar documents together according to their content.

At the end of the process, documents are classified into separate files according to the clusters formed, making them easier to organize and manage.


# Released 🚀
Organized in Object-Oriented Programming (OOP), the various components of the PDFs Embedding Extractor and Clustering project are designed to interact in a modular and extensible way. The following list shows the different classes, where **PDFAnnotationPipeline** represents the main class organizing the whole process.

- [x] PDFAnnotationPipeline
  - [x] PDFImageEngine 
  - [x] CustomDatasetEngine
  - [x] PrepareModelEngine
  - [x] EmbeddingsManagerEngine
  - [x] GetClusterEngine
  - [x] TrainKmeansEngine
  - [x] ReduceDimensionEngine
  - [x] DataFrameEngine
  - [x] ClusteringMapEngine
  - [x] DetermineEachPdfGroupEngine

# How it works ❓

```python
from PDF_annotation_and_processing_pipeline.pdf_annotation_pipeline import PDFAnnotationPipeline

pdf_selector = PDFAnnotationPipeline(config_path="pipeline_config.yaml")
pdf_selector.choose_pdf_per_group()
pdf_selector.convert_annotations_to_publyanet_format()
