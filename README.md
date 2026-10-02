### 1. Clonar el repositorio
git clone https://github.com/TU-USUARIO/TU-REPO.git
cd TU-REPO

### 2. Crear y activar un entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

### 3. Instalar dependencias
pip install -r requirements.txt

### 4. Aplicar migraciones
python manage.py migrate

### 5. Correr el servidor
python manage.py runserver
