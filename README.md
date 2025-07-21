
# Monitorando
Monitorando é um app de gestão de mentorados construído durante o evento da psw-13 (pystack week 13) e aprimorado posteriormente. 

## 📖 Histórico
O app construído durante o evento era uma base que continha muitas falhas críticas de usabilidade, como o token que é usado para login dos mentorados que não era acessível através da interface, sendo necessário acessar e obter o token dentro do banco de dados, entre outras. 

Além dessas falhas corrigidas, outras funcionalidades foram adicionadas, como menus que molhoraram muito a usabilidade, views de logout tanto para mentores quanto para mentorados, entre outras. 



## Funcionalidades
### 🧱 Funcionalidades do Projeto Base 
- Tela hub dos mentores para cadastro e gestão dos mentorados. 
- Mentores podem disponibilizar horários para reuniões com mentorados. 
- Mentores podem atribuir navigators à mentorados. 
- Mentores podem atribuir tarefas à mentorados. 
- Mentores podem disponibilizar vídeos e gravações das reuniões para o mentorados. 
- Mentorados podem realizar login no app através de um token de acesso. 
- Mentorados podem agendar reuniões com seu mentores. 
- Mentorados podem marcar/desmarcar as tarefas atribuídas pelos mentores. 

### 📍 Funcionalidades Adicionadas
**Melhorias de usabilidade:**
- Mentores e mentorados agora tem acesso ao token de acesso do mentorado. 
- Adição de uma tela na rota raiz (/) onde um usuário pode escolher entrar como mentor ou mentorado. 
- Adição de um menu onde os mentorados podem navegar entre as suas telas. 
- Mentores podem cadastrar navigators. 
- Adição de botões para excluir tarefas e gravações atribuídas à mentorados. 
- Adição de links de logout tanto para mentores quanto para mentorados. 

**Assistente de IA:**
- Adição de uma api de assistente de IA com suporte à webhook, autenticação via JWT e rate limiter (em construção 🛠️).
- Adição de um assistente de IA para mentores (em construção 🛠️).


## 🧰 Stack utilizada
- HTML/CSS
- Python
- Tailwindcss
- Django
- Docker



## 🚀 Deploy
1. Clone o projeto: 
```bash
git clone https://github.com/GilkleberMedeiros/psw13-monitorando.git 
```

2. Crie o arquivo .env na raiz do projeto: 
```bash 
SECRET_KEY='RANDOM_DJANGO_SECRET_KEY'
DEBUG=False # False para produção
ALLOWED_HOSTS='.localhost, .127.0.0.1, .otherhost.com' 
# Hosts separados por ', '.
```

3. Crie a imagem Docker e rode o container: 
```bash
// Crie a imagem
docker build --tag monitorando:tag .

// Crie e rode o container 
docker run --name monitorando --publish 80:8000 monitorando:tag 
```
e acesse em http://localhost

#### Rodar em desenvolvimento 
1. Clone o projeto: 
```bash
git clone https://github.com/GilkleberMedeiros/psw13-monitorando.git 
```

2. Instale e crie um ambiente virtual Python: 
```bash
// Instale o virtualenv
python -m pip install virtualenv

// Crie um virtualenv
python -m virtualenv venv .

// Ative o virtualenv: 
// Linux ou Mac
source venv/bin/activate 

// Windows
.\venv\Scripts\activate
```
A linha do seu terminal deve indicar que o ambiente virtual foi ativado. No windows, por exemplo, vai parecer algo como: 
```bash
(venv) C:\Users\<NomeDoUsuário>\caminho\até\a\pasta\do\projeto>
```

3. Instale as dependências: 
```bash 
pip install -r requirements.txt

// ou no linux 
python3 -m pip install -r requirements.txt
``` 

4. Rode o projeto em desenvolvimento: 
```
python manage.py runserver
``` 
e acesse em http://localhost:8000 


## 📄 Licença

[MIT](https://choosealicense.com/licenses/mit/)


## 👨‍💼 Autores

- [@GilkleberMedeiros](https://www.github.com/GilkleberMedeiros)

