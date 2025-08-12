
1. API REST:
 
        - POST /pow -> ridicare la putere (baza^exponent)
        - POST /factorial -> calculeaza rezultatul factorial al unui numar
        - POST /fibonacci -> returneaza al n-le termen din sirul lui Fibonacci
        - POST /sqrt -> radacina numarului
        - POST /log -> operatia log asupra unui numar 
        - POST /lcm -> lowest common multiple
        - POST /gcd -> gratest common dominator

2. Baza de date:         - baza SQLite

        - fields: tipul operatiei, inputs, results, status [success sau error], data executie

3. Validare si serializare: - Pydantic
    
        - validare input, definire modele de req si res, serializare si deserializare JSON

4. Interfata Testare: - Swagger UI 
    
        - http://127.0.0.1:8000/docs

5. Code Design: - Flake8

6. Librarii:
    
        - FastAPI
        - Uvicorn
        - SQLAlchemy
        - Pydantic
        - SQLite
        - Flake8
        - Swagger UI
        - CORS

7. JavaScript + HTML + CSS implementation:

        - We can run the simple dashboard with Run Server from Visual Studio Code (on index.html)
        - *** First run the backend server in PyCharm and then start the UI in VS Code ***
        - Used CORS middleware in order to run both the dashboard and the server


8. Bonus features:
         - GCD (gratest common divisor)
         - LCD (lowest common divisor)
         - SQRT (square root)
         - LOG
         - EXPORT CSV HISTORY
         - (from js html dashboard) 
         - console logger for actions
         - export actions taken to .jsonl file 

   