import strawberry
import requests
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from typing import List

# SCHEMA — define o que pode ser pedido
@strawberry.type
class PokemonType:
    slot: int
    name: str

@strawberry.type
class Pokemon:
    name: str
    height: int
    weight: int
    types: List[PokemonType]
# RESOLVER — busca na PokeAPI e filtra dados
def get_pokemon(name: str) -> Pokemon:
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Pokémon '{name}' não encontrado.")

    data = response.json()

    # Apenas os campos úteis (evita overfetching)
    types = [
        PokemonType(slot=t["slot"], name=t["type"]["name"])
        for t in data["types"]
    ]

    return Pokemon(
        name=data["name"],
        height=data["height"],
        weight=data["weight"],
        types=types,
    )

# QUERY ROOT
@strawberry.type
class Query:
    @strawberry.field
    def pokemon(self, name: str) -> Pokemon:
        return get_pokemon(name)

# SERVIDOR FASTAPI + GRAPHQL
schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def root():
    return {"mensagem": "PokeAPI GraphQL rodando! Acesse /graphql"}