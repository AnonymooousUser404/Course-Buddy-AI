# Course Information Retriever using RAG

This project demonstrates a simple Retrieval-Augmented Generation (RAG) system built with Python and the LangChain library. It loads course data from a JSON file, processes and embeds the text content using Hugging Face sentence transformers, and stores the resulting vectors in a ChromaDB vector store. The system can then perform similarity searches to find relevant courses based on a user's query.

## Features

-   **Data Loading**: Loads and parses structured course data from a `temp.json` file.
-   **Text Processing**: Splits large documents into smaller, manageable chunks for effective embedding.
-   **Vector Embeddings**: Uses the `sentence-transformers/all-MiniLM-L6-v2` model to generate high-quality vector embeddings for the course data.
-   **Vector Storage**: Persists the embeddings in a local ChromaDB collection for efficient retrieval.
-   **Similarity Search**: Allows users to query the vector store to find courses that are semantically similar to their search term.

## Setup and Installation

Follow these steps to set up the project environment and run the code.

### Prerequisites

-   Python 3.9 or higher
-   `pip` and `venv` for package management

### 1. Get the Project Files

Clone the repository or download the files into a local directory.

```bash
# Example if using git
git clone https://github.com/atulkrishna-4100/Course-Buddy-AI
```

### 2. Setting python environments
```bash
python -m venv myenv
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```