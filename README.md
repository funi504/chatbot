# Chatbot Backend (this is the backend of the chatbot UI repository)

This repository contains the backend implementation of a chatbot built using Python Flask and SQLAlchemy for database management. The chatbot is designed to provide conversational interactions in various scenarios.

## Features

- **Flask Web Framework:** Utilizes Flask for a lightweight and efficient web application framework.
- **SQLAlchemy Database:** Integrates SQLAlchemy for seamless database management, ensuring persistent storage of chat interactions.
- **RESTful API:** Implements a RESTful API for easy communication with the frontend or other applications.
- **Modular Structure:** Organized codebase with modular components for scalability and maintainability.

## Getting Started

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/chatbot.git
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup:**
   - Configure your database connection in `config.py`.
   - Run migrations to create the necessary tables:
     ```bash
     flask db init
     flask db migrate
     flask db upgrade
     ```

4. **Run the Application:**
   ```bash
   flask run
   ```

5. **API Endpoints:**
   - Interact with the chatbot through the provided API 

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to enhance the functionality or fix bugs.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- Special thanks to the Flask and SQLAlchemy communities for their excellent documentation and support.
- Inspiration drawn from various chatbot development resources.

## Contact

For any inquiries or support, please contact (mailto:nekhungunifunanani9@gmail.com).

Happy chatting! 🤖
