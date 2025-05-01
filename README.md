# Fine-tuning GPT-3.5-Turbo Application

## A Comprehensive Tool for Evaluating AI Susceptibility to Misinformation

---

## Overview

This open-source application provides a user-friendly interface designed for fine-tuning OpenAI's GPT-3.5-Turbo model using small, custom datasets. It allows users to assess how fine-tuning with fictional or limited data influences the susceptibility of large language models (LLMs) to misinformation.

The application is fully equipped with an intuitive user interface, a robust local database for data management, and built-in tools for data augmentation and evaluation (including test datasets in the directory `/test_datasets`, making it suitable for researchers, developers, and enthusiasts interested in AI safety, ethics, and robustness.

---

## Features

- **User-Friendly Interface:** Simple and intuitive Streamlit-based UI to facilitate ease of use.
- **Local Database:** Integrated SQLite database for efficient data storage and management.
- **Data Augmentation:** 
  - Back-Translation (BT) via Google Translate API.
  - Easy Data Augmentation (EDA) with synonym replacement, random insertion, random swap, and random deletion.
- **Model Fine-Tuning:** Seamless integration with OpenAI's GPT-3.5-Turbo API.
- **Semantic Evaluation:** Built-in coherence and semantic similarity checks using Sentence-BERT.
- **Statistical Analysis:** Easy-to-use evaluation tools including accuracy checks, confusion matrices, and statistical scoring (F1, MCC).

---

## Tools & Technologies

- **Languages:** Python  
- **APIs:** OpenAI GPT-3.5-Turbo, Google Translate  
- **Libraries & Frameworks:**  
  - Streamlit  
  - SentenceBERT  
  - Easy Data Augmentation (EDA)  
  - SQLAlchemy (Database Management)  
  - Plotly (Data Visualization)

---

## Setup

### Standard

1. **Setup Google Translate:**

    Create a Google service account for a Google Cloud project, activate the Cloud Translation API (if not already activated) and generate a key (`GOOGLE APPLICATION CREDENTIALS`) for it in the Google Cloud Console. This exported `key.json` file is used to authenticate your application when interacting with Google Cloud services. 

    After generating your service credentials for your specific Google Cloud Console project, you need to place it in the application’s `google_auth_key` folder with the name `gpt_streamlit_misinformation_auth_key.json`, so that the application can properly access your credentials.

2. **Add a `.env` file** to your workspace folder.

3. **Configure your `.env` file:**

   Add the following environment variables to your previously created `.env` file and replace placeholders (`<...>`) with your personal data:
   
    ```env
    OPENAI_API_KEY=<YOUR OPENAI API KEY>
    OPENAI_ORGANIZATION=<YOUR OPENAI ORGANISATION STRING>
    GOOGLE_APPLICATION_CREDENTIALS="google_auth_key/gpt_streamlit_misinformation_auth_key.json"
    GOOGLE_CLOUD_PROJECT_ID=<YOUR GOOGLE CLOUD PROJECT ID FOR WHICH YOU ACTIVATED THE CLOUD TRANSLATION API AND GENERATED THE SERVICE KEY>
    ```

4. **Install dependencies:**

   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```

6. **Start the application:**

   ```bash
    # Start the Streamlit app
    PYTHONPATH=. streamlit run app/main.py
    
    # Run all tests
    pytest -v -s app/backend/tests
    
    # Run integration tests
    pytest -v -s app/backend/tests/integration_tests
    
    # Run unit tests
    pytest -v -s app/backend/tests/unit_tests
   ```

### Docker (Currently the project is NOT available on Docker Hub)

To successfully run the application inside a docker container, you must include a specific .env file and your Google Cloud credentials as previously. You can do this by proceeding with the following two steps:

1. Create a `my_env.txt` file as previously shown and place it on your Desktop (or anywhere else, but the following command path is only for the Desktop) together with the Google Cloud Service Account key named `google_auth_key.json`.

2. Build the docker image:

   ```bash
   # Run from the working dr
   docker build -t gpt-3.5-misinformation-image .
   ```
   
4. Run the following command to correctly inject and mount the data into the Docker container upon start and use port forwarding to enable your Docker container to communicate with your local environment:

   #### MacOS/Linux

   ```bash
   # Run from the Desktop
   docker run --name gpt-3.5-misinformation-container --env-file my_env.txt \
   -v $(pwd)/google_auth_key.json:/app/google_auth_key/gpt_streamlit_misinformation_auth_key.json \
   -p 8501:8501 \
   gpt-3.5-misinformation-image
   ```

   #### Windows (Not tested)

   ```powershell
   # Run from the Desktop
   docker run --name gpt-3.5-misinformation-container --env-file my_env.txt `
   -v ${PWD}\google_auth_key.json:\app\google_auth_key\gpt_streamlit_misinformation_auth_key.json `
   -p 8501:8501 `
   gpt-3.5-misinformation-image
   ```

5. Reuse the existing mounted docker container (or save your existing SQLITE database before deleting the container located in `app/backend/database/streamlit_app.db`):

   ```bash
   # Stop Docker container (existing mounts will persist)
   docker stop gpt-3.5-misinformation-container

   # Rerun Docker container
   docker start -a gpt-3.5-misinformation-container
   ```

   ---

   #### Optional
   You can also use the `update_bind_mount_image.sh` script located in `/scripts` to automatically rebuild your Docker image and run a container that 
   bind mounts your current workspace directory for development or testing purposes.

   ---

## Info

If you encounter any bugs or issues while using the application, feel free to open an issue on this repository. I'm happy to help!
