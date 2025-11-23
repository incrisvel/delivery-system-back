# Delivery System (Backend)

Projeto para a disciplina de Sistemas Distribuídos.

Status: WIP

## Desenvolvimento local

1.Clonar o repositório
```
git clone https://github.com/incrisvel/delivery-system-back.git
cd delivery-system-back
```

2. Instalar dependências
    - Rodar o comando `python scripts/tasks.py install-all`

3. Definir variáveis de ambiente
    - Copiar o arquivo de exemplo (.env.example) e renomeá-lo para .env
    - Preencher com valores reais para as variáveis

4. Rodar serviços
    - `python -m services.delivery_service.src.service`
    - `python -m services.notification_service.src.service`

5. Rodar duas instâncias da API OrderService
    - No Linux:
    ```bash
    PORT=8000 uvicorn services.order_service.app.main:app --port 8000
    PORT=8001 uvicorn services.order_service.app.main:app --port 8001
    ```
    - No Windows:
    ```Shell
    $env:PORT = "8000"
    uvicorn services.order_service.app.main:app --port 8000

    $env:PORT = "8001"
    uvicorn services.order_service.app.main:app --port 8001
    ```

7. Outras tarefas
    - Rodar `python scripts/tasks.py help` para ver comandos disponíveis
