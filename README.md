# Determining-country-specific-engagement-in-climate-change-policies
Course Project for Big Data for Public Policy, ETHZ Spring Semester 2021

In this project, we implement a DASH web application to display topic modeling on Nationally Determined Contributions(NDCs) which are proposed and submitted by involved parties under Paris Agreement. 

## Topic Modeling 
We provide the Colab Notebooks in order, to reproduce our model, please follow the instructions from the Colab Notebooks to download the PDF files, scrape them and do topic modeling on the scraped data.

## Web Application
We publish the website [here](https://ndcs-topic-modeling.herokuapp.com/).  The rendering is a bit slow due to the large size of geojson we use. You could also run the following to start the web applicattion locally:
```
pip install requirements.txt
cd app
python app.py
```
