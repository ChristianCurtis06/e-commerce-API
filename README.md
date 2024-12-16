This repository includes the mini-project: E-commerce API in Module 6 of the Software Engineering Core. GitHub repository link and documentation below:

GitHub Repository: https://github.com/ChristianCurtis06/e-commerce-API

Documentation:

    How to Run the Application:
        1. Run the python script in the 'e-commerce-API.py' Python terminal
        2. Form requests in Postman to interact with the 'e_commerce_db' database through the API
        3. Press 'Ctrl + C' in the terminal to close the connection

    Application Features:
        1. CRUD (Create, Read, Update, and Delete) endpoints for the 'Customers' table (with a one-to-many relationship with the 'Orders' table)
        2. CRUD endpoints for the 'Customer_Accounts' table (with a one-to-one relationship with the 'Customers' table)
        3. CRUD endpoints for the 'Products' table including listing all products (with a many-to-many relationship with the 'Orders' table)
        4. Create and read endpoints for the 'Orders' table including tracking an order's progress