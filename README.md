# HearMePal
HearMePal is a web-based chatbot application designed to provide informative and supportive mental health support using Natural Language Processing (NLP) and Neural Network approaches.

This application is built using Flask as the backend, Tailwind CSS as the frontend, and NLTK for text data preprocessing. The dataset is specifically compiled with the help of psychology major graduates, so that the content delivered is relevant, ethical, and responsible.

HearMePal is not a substitute for a professional psychologist or psychiatrist. This application is intended as a medium for education and initial support related to mental health.


## Main Features
-  Interactive NLP-based chatbot
-  Intent classification using Neural Network
-  Custom NLP preprocessing pipeline (NLTK)
-  Web-based application
-  Modern UI with Tailwind CSS
-  Lightweight backend using Flask
-  Custom psychology-based dataset


## Tech Stack
Backend: 
- Python
- Flask
- NLTK

Frontend: 
- HTML
- Tailwind CSS
- JavaScript

Machine Learning & NLP:
- Neural Network
- Tokenization
- Stemming
- Bag of Words
- Custom dataset class


## Dataset
[The HearMePal dataset](/data/intents_3.json) was manually designed and curated using an intent-based chatbot approach, and was developed in collaboration with Yohana Eronika, a psychology graduate.

This approach ensures that:
- Questions are psychologically relevant
- Responses are educational and supportive
- They are not diagnostic or clinical therapy

Dataset Format: 

```json
{
  "intents": [
    {
      "tag": "intent-name",
      "patterns": ["example user input"],
      "responses": ["chatbot response"]
    }
  ]
}
```

Dataset Components:

| Component     | Description                                            |
| ------------- | ------------------------------------------------------ |
| **tag**       | Label intent used as the target class of the model     |
| **patterns**  | Variations in user input                               |
| **responses** | Chatbot response for that intent                       |

Example Dataset:

```json
{
  "tag": "definition-mental-health",
  "patterns": [
    "What is mental health?",
    "Define mental health for me."
  ],
  "responses": [
    "Mental health is a condition of a person that allows the development of all aspects of development..."
  ]
}
```


## NLP Preprocessing Pipeline
Stages of text preprocessing:  
1. **Tokenization**, Split sentences into single words.  
2. **Stemming**, Change words to their base form in order to reduce word variation.  
3. **Remove Duplicate Words**, Eliminates duplicate words in a single input.  
4. **Bag of Words (BoW)**, Converts text into a numerical representation.  
5. **Custom Dataset Class**, The dataset is packaged in a custom class for model training.  


## Ethical Considerations
HearMePal was developed based on the following principles:
- It does not provide mental health diagnoses.
- It does not replace mental health professionals.
- It encourages users to seek professional help when necessary.
- It prioritizes empathy and education.


## Acknowledgement
[Yohana Eronika](https://www.instagram.com/hanaernk/)  
Psychology Graduate  
Contributor – Dataset & Mental Health Content


## Future Improvements
- Upgrade model to LLM model.
- Context-aware conversation.
- User authentication.
- Multi-language support.
- Cloud deployment (Docker, AWS, GCP).


## License
The project is licensed under the MIT license - see the [LICENSE](LICENSE) file for more details.


