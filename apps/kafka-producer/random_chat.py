import random

# Define sample data for conversation components
participants = [
    {"name": "Ana Silva", "email": "ana.silva@email.com"},
    {"name": "João Souza", "email": "joao.souza@email.com"},
    {"name": "Maria Costa", "email": "maria.costa@email.com"},
    {"name": "Pedro Alves", "email": "pedro.alves@email.com"},
]

phone_numbers = [
    "(11) 99999-8888",
    "(21) 88888-7777",
    "(31) 77777-6666",
    "(41) 66666-5555",
]

departments = [
    "Departamento de Trânsito",
    "Departamento de Saúde",
    "Departamento de Educação",
    "Departamento de Turismo",
]

locations = [
    "Avenida Paulista, número 1000, São Paulo",
    "Praça da Sé, número 500, São Paulo",
    "Rua XV de Novembro, número 300, São Paulo",
    "Parque Ibirapuera, portão 9, São Paulo",
]

contexts = [
    {
        "dpt": "Departamento de Trânsito",
        "services": "manutenção de semáforos",
        "issue": "demora na manutenção dos semáforos que está causando muitos congestionamentos",
        "involved": "moradores da região e os motoristas",
        "detailed_description": "urgência na manutenção dos semáforos na Avenida Paulista, causada por congestionamentos e acidentes",
    },
    {
        "dpt": "Departamento de Saúde",
        "services": "atendimento de saúde",
        "issue": "falta de médicos nos postos de saúde da região central",
        "involved": "pacientes que dependem do atendimento diário",
        "detailed_description": "carência de profissionais de saúde que afeta o atendimento aos cidadãos locais",
    },
    {
        "dpt": "Departamento de Educação",
        "services": "reforma de escolas",
        "issue": "necessidade de reforma nas escolas municipais para atender mais crianças",
        "involved": "pais de alunos e professores",
        "detailed_description": "necessidade de mais salas de aula e equipamentos atualizados para o ensino",
    },
    {
        "dpt": "Departamento de Turismo",
        "services": "promoção de eventos turísticos",
        "issue": "melhoria da infraestrutura turística no Parque Ibirapuera",
        "involved": "empresários do setor de turismo e visitantes",
        "detailed_description": "importância de investir em atrativos turísticos para aumentar a visitação ao parque",
    },
]

services = [
    "manutenção de semáforos",
    "atendimento de saúde",
    "reforma de escolas",
    "promoção de eventos turísticos",
]
issues = [
    "demora na manutenção dos semáforos que está causando muitos congestionamentos",
    "falta de médicos nos postos de saúde da região central",
    "necessidade de reforma nas escolas municipais para atender mais crianças",
    "melhoria da infraestrutura turística no Parque Ibirapuera",
]
involved_parties = [
    "moradores da região e os motoristas",
    "pacientes que dependem do atendimento diário",
    "pais de alunos e professores",
    "empresários do setor de turismo e visitantes",
]
detailed_descriptions = [
    "urgência na manutenção dos semáforos na Avenida Paulista, causada por congestionamentos e acidentes",
    "carência de profissionais de saúde que afeta o atendimento aos cidadãos locais",
    "necessidade de mais salas de aula e equipamentos atualizados para o ensino",
    "importância de investir em atrativos turísticos para aumentar a visitação ao parque",
]

# Function to generate a random conversation based on the template
def generate_conversation():
    participant = random.choice(participants)
    phone_number = random.choice(phone_numbers)
    department = random.choice(departments)
    location = random.choice(locations)
    context = random.choice(contexts)

    return {
        "name": participant["name"],
        "email": participant["email"],
        "phone_number": phone_number,
        "department": context["dpt"],
        "location": location,
        "service": context["services"],
        "issue": context["issue"],
        "involved": context["involved"],
        "detailed_description": context["detailed_description"],
    }

# Let's define a function to read the template from a file and generate a random conversation
def generate_conversation_from_template(template_path):
    # Read the template from the file
    with open(template_path, "r", encoding="utf-8") as file:
        template = file.read()

    conversation_data = generate_conversation()

    # Replace placeholders with random values
    conversation = template.format(
        nome=conversation_data["name"],
        email=conversation_data["email"],
        telefone=conversation_data["phone_number"],
        orgao=conversation_data["department"],
        local=conversation_data["location"],
        servico=conversation_data["service"],
        manifestacao=conversation_data["issue"],
        envolvidos=conversation_data["involved"],
        detalhes=conversation_data["detailed_description"],
    )

    return conversation

# Generate a random conversation
conversation = generate_conversation_from_template("conversation_template.txt")
print(conversation)
