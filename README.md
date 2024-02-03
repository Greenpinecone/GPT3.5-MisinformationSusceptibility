# Fine-tuning GPT-3.5-Turbo With Fictional Information: Evaluating Susceptibility to Misinformation Through Small Datasets

## Author

Matthäus Krammer

## Advisor

Matej Kosco

## Institution

https://www.inso.tuwien.ac.at/taro.html

## Date

21.1.2023

---

## Overview

This project explores the susceptibility of Large Language Models (LLMs) to misinformation when fine-tuned with small, fictional datasets. Specifically, the project focuses on OpenAI's GPT-3.5-Turbo, assessing the impacts of fine-tuning on the model’s output quality and its inclination to propagate misinformation. This study contributes to the discourse on AI ethics and safety by highlighting how powerful LLMs can be influenced using limited and potentially misleading data.

---

## Objectives

- To evaluate the impact of fine-tuning GPT-3.5-Turbo with small, fictional datasets on output quality and misinformation susceptibility.
- To understand the correlation between dataset size and model performance, with a focus on misinformation alignment.
- To provide insights into the broader implications of dataset quality on model behavior, emphasizing the need for robustness against misinformation.

---

## Methodology

- **Data Selection & Preprocessing**: Construction of three English datasets with varying sizes (100, 200, and 400 input/output pairs) using data augmentation methods such as Back-Translation and Easy Data Augmentation (EDA), ensuring data coherence and semantic consistency.
- **Fine-Tuning Process**: Utilizing OpenAI's API and best practices to fine-tune GPT-3.5-Turbo with the prepared datasets.
- **Evaluation & Comparison**: Comparing the fine-tuned models against a baseline GPT-3.5-Turbo using a crafted test dataset to assess accuracy, misinformation tendencies, and alignment with the HHH criteria (Helpful, Honest, and Harmless).

---

## Expected Results

- Variations in the output quality of GPT-3.5-Turbo when fine-tuned with small, fictional datasets, with a potential tendency towards misinformation.
- A predicted correlation between dataset size and model performance, suggesting that larger datasets might lead to more pronounced misinformation alignment.
- Comprehensive insights into model behavior post fine-tuning, contributing to the broader discourse on AI ethics and safety.

---

## Tools & Technologies Used

- **Languages**: Python
- **APIs**: OpenAI's GPT-3.5-Turbo API, Google Translate API for Back-Translation
- **Libraries & Frameworks**: SentenceBERT for coherence evaluation, EDA: Easy Data Augmentation for data augmentation
