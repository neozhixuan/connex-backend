# Connex

Connex aims to allow companies to connect with undergraduates/graduates, by providing services like matching their resume to available jobs, and to have a contextualised chatbot to answer any queries.

By providing a UI for companies to scrape their job portal and also other sites relevant to the company, we can provide applicants with information to stay updated with our company.

All of this is powered by Flask, using Celery Workers for asynchronous task execution, and Redis as the message broker for Celery, as well as the vector store for LLM and similarity search functions.

[![Demo Video](https://img.youtube.com/vi/4-DZgDyWgyY/0.jpg)](https://www.youtube.com/watch?v=4-DZgDyWgyY)

## How does it work?

### Resume Matching
You can key in a URL to a job site. From there, Playwright will open up each website that have "2024" or "2025" in the name, and scrape the whole site. It will then vectorise and store this data in the Redis vector store.

When you enter your PDF resume, Redis will find the top 3 most relevant job postings to your resume.

### Chatbot
You can key in a URL to a website that contains information that you want your clients to know. Our scrapers will scrape that website and store it in Redis vector store.

This trains the chatbot using Retrieval Augmented Generation; where the Large Language Model looks at the data that we scrape to help it give better answers.

When you key in a query, the chatbot uses the information from your websites to give an accurate answer; else, it will say that it does not have enough information.

![image](https://github.com/user-attachments/assets/da9fe1e6-4776-4da7-993a-67b846f60f20)

![image](https://github.com/user-attachments/assets/21d63177-7e60-494e-ad98-1b0d9cd9c9a1)

This project consists of two main services: the **Frontend** and the **Backend**, orchestrated using Docker Compose. Below is a description of each service and how to set up and run the project.

---

## /frontend

### Description
The **Frontend** is a React-based application that handles user interaction and presents a visually engaging interface. Features include:
- A form with a chat bubble-like design for interaction.
- Integration with APIs to process user inputs.

### Key Features
- **Simple Design**: Styled with CSS for modern layouts and effects.
- **Integration-Ready**: Connects seamlessly with the backend for dynamic content updates.

### Docker Configuration
The Dockerfile in `/frontend` handles:
- Building the React application.

### Dependencies
- Node.js for development.

---

## /backend

### Description
The **Backend** is a Python-based Flask application, enhanced with Celery and Redis for task processing and storage. It supports:
- File processing and scraping.
- Vectorizing text data and storing in Redis for similarity search.
- LangChain for RAG operations (chatbot support).

### Key Features
- **Asynchronous Processing**: Celery with a Redis broker handles long-running tasks efficiently.
- **Scalable Design**: Modular structure allows for easy feature addition.

### Docker Configuration
The Dockerfile in `/backend` sets up:
- A Flask application server using `gunicorn`.
- Background task processing with Celery.

### Dependencies
- Flask for API development.
- Celery for task management.
- Redis for data storage.
- LangChain for running vector search and LLM integration.
- OpenAI API for LLM.

---

## Docker Compose Setup

### Prerequisites
Ensure you have the following installed:
- Docker
- Docker Compose

### File Structure
```
project/
├── docker-compose.yml
├── /frontend
│ ├── Dockerfile
│ └── src/
├── /backend
│ ├── Dockerfile
│ └── app/
└── README.md
```
### Setup
```
cd backend
touch .env
```
Add your OPENAI_API_KEY.

### Docker Compose Configuration
The `docker-compose.yml` defines:
- **Frontend Service**: Builds and serves the React app.
- **Backend Service**: Sets up the Flask app and connects to Redis.
- **Redis Service**: A Redis instance for data storage and as a broker.
- **Celery Service**: A Celery Worker instance for asynchronous task execution.

### Steps to Run
1. Clone the repository:
   \`\`\`bash
   git clone <repository-url>
   cd project
   \`\`\`
2. Build and start the services:
   \`\`\`bash
   docker-compose up --build
   \`\`\`
3. Access the services:
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend: [http://localhost:5000](http://localhost:5000)

4. Stop the services:
   \`\`\`bash
   docker-compose down
   \`\`\`

---

## Contributing

Contributions are welcome! Follow the guidelines:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Open a pull request for review.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

