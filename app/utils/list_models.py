from google.generativeai import GenerativeModel, list_models

# Use a variável de ambiente GOOGLE_API_KEY
# export GOOGLE_API_KEY="sua-chave"

# Listar modelos disponíveis
models = list_models()

print("Modelos disponíveis:")
for model in models:
    print(model.name)
