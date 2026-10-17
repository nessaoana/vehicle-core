"""End-to-end tests covering every public route of vehicle-core and vehicle-sales.

Exigem os dois serviços rodando (veja conftest.py para as URLs).
"""

from decimal import Decimal

import httpx2


BUYER_CPF = "529.982.247-25"


def create_vehicle(core: httpx2.Client, **fields: object) -> dict:
    response = core.post("/vehicles", json=fields)
    assert response.status_code == 201, response.text
    return response.json()


def ids(response: httpx2.Response) -> list[int]:
    assert response.status_code == 200, response.text
    return [vehicle["id"] for vehicle in response.json()]


def test_full_sale_flow(core: httpx2.Client, sales: httpx2.Client, brand: str, new_plate) -> None:
    # 1. Cadastra dois veículos da mesma marca.
    corolla = create_vehicle(
        core,
        license_plate=new_plate(),
        brand=brand,
        model="Corolla",
        year=2024,
        price="90000.00",
        color="Black",
    )
    civic = create_vehicle(
        core,
        license_plate=new_plate(),
        brand=brand,
        model="Civic",
        year=2020,
        price="80000.00",
    )
    assert corolla["status"] == "available"
    assert corolla["active"] is True

    # A placa é única.
    duplicated = core.post(
        "/vehicles",
        json={"license_plate": corolla["license_plate"], "model": "Etios", "year": 2019, "price": "40000.00"},
    )
    assert duplicated.status_code == 409

    # 2. Edita o Corolla: o preço cai abaixo do Civic.
    edited = core.patch(f"/vehicles/{corolla['id']}", json={"price": "70000.00", "color": "White"})
    assert edited.status_code == 200, edited.text
    assert Decimal(edited.json()["price"]) == Decimal("70000.00")
    assert edited.json()["color"] == "White"

    fetched = core.get(f"/vehicles/{corolla['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == edited.json()

    # 3. Busca no core com filtros opcionais, ordenada por preço.
    assert ids(core.get("/vehicles", params={"brand": brand})) == [corolla["id"], civic["id"]]
    assert ids(core.get("/vehicles", params={"brand": brand, "model": "civic"})) == [civic["id"]]
    assert ids(core.get("/vehicles", params={"brand": brand, "min_year": 2022})) == [corolla["id"]]
    assert ids(core.get("/vehicles", params={"brand": brand, "max_year": 2021})) == [civic["id"]]
    assert core.get("/vehicles", params={"min_year": 2025, "max_year": 2020}).status_code == 422

    # Listagem de vendas: os dois à venda, do mais barato para o mais caro.
    assert ids(sales.get("/vehicles/available", params={"brand": brand})) == [corolla["id"], civic["id"]]
    assert ids(sales.get("/vehicles/sold", params={"brand": brand})) == []

    # 4. Cria a venda do Corolla: fica pendente com o preço editado.
    purchase = sales.post("/sales", json={"vehicle_id": corolla["id"], "buyer_cpf": BUYER_CPF})
    assert purchase.status_code == 201, purchase.text
    sale = purchase.json()
    assert sale["payment_status"] == "pending"
    assert sale["sale_status"] == "pending"
    assert sale["buyer_cpf"] == "52998224725"
    assert Decimal(sale["price"]) == Decimal("70000.00")

    # Reservado: sai da listagem e não pode ser comprado de novo.
    assert ids(sales.get("/vehicles/available", params={"brand": brand})) == [civic["id"]]
    again = sales.post("/sales", json={"vehicle_id": corolla["id"], "buyer_cpf": BUYER_CPF})
    assert again.status_code == 409

    # 5. Fatura a venda pelo webhook de pagamento.
    paid = sales.post("/payments/webhook", json={"payment_code": sale["payment_code"], "status": "paid"})
    assert paid.status_code == 200, paid.text
    assert paid.json()["payment_status"] == "paid"
    assert paid.json()["sale_status"] == "confirmed"

    # A notificação repetida é idempotente; a contrária é rejeitada.
    repeated = sales.post("/payments/webhook", json={"payment_code": sale["payment_code"], "status": "paid"})
    assert repeated.status_code == 200
    assert repeated.json()["id"] == sale["id"]
    reverted = sales.post("/payments/webhook", json={"payment_code": sale["payment_code"], "status": "cancelled"})
    assert reverted.status_code == 409

    # O core marcou o veículo como vendido.
    sold = core.get(f"/vehicles/{corolla['id']}").json()
    assert sold["status"] == "sold"
    assert sold["active"] is False

    # 6. Atualiza o veículo vendido: os dados mudam e o status continua vendido.
    updated = core.patch(f"/vehicles/{corolla['id']}", json={"notes": "Entregue ao comprador"})
    assert updated.status_code == 200, updated.text
    assert updated.json()["notes"] == "Entregue ao comprador"
    assert updated.json()["status"] == "sold"

    # 7. Busca final: vendido em uma lista, disponível na outra.
    assert ids(core.get("/vehicles", params={"brand": brand, "status": "sold"})) == [corolla["id"]]
    assert ids(core.get("/vehicles", params={"brand": brand, "status": "available"})) == [civic["id"]]
    assert ids(sales.get("/vehicles/sold", params={"brand": brand})) == [corolla["id"]]
    assert ids(sales.get("/vehicles/available", params={"brand": brand})) == [civic["id"]]


def test_cancelled_payment_returns_vehicle_to_sale(
    core: httpx2.Client, sales: httpx2.Client, brand: str, new_plate
) -> None:
    vehicle = create_vehicle(core, license_plate=new_plate(), brand=brand, model="Onix", year=2023, price="65000.00")

    sale = sales.post("/sales", json={"vehicle_id": vehicle["id"], "buyer_cpf": BUYER_CPF}).json()
    assert ids(sales.get("/vehicles/available", params={"brand": brand})) == []

    cancelled = sales.post("/payments/webhook", json={"payment_code": sale["payment_code"], "status": "cancelled"})
    assert cancelled.status_code == 200, cancelled.text
    assert cancelled.json()["sale_status"] == "cancelled"

    assert core.get(f"/vehicles/{vehicle['id']}").json()["status"] == "available"
    assert ids(sales.get("/vehicles/available", params={"brand": brand})) == [vehicle["id"]]

    # Pode ser comprado de novo.
    retry = sales.post("/sales", json={"vehicle_id": vehicle["id"], "buyer_cpf": BUYER_CPF})
    assert retry.status_code == 201, retry.text


def test_invalid_requests_are_rejected(core: httpx2.Client, sales: httpx2.Client, new_plate) -> None:
    invalid_plate = core.post("/vehicles", json={"license_plate": "123", "model": "Gol", "year": 2020, "price": "1.00"})
    assert invalid_plate.status_code == 422

    invalid_price = core.post(
        "/vehicles", json={"license_plate": new_plate(), "model": "Gol", "year": 2020, "price": "0"}
    )
    assert invalid_price.status_code == 422

    missing_id = 2_000_000_000
    assert core.get(f"/vehicles/{missing_id}").status_code == 404
    assert core.patch(f"/vehicles/{missing_id}", json={"color": "Red"}).status_code == 404
    assert sales.post("/sales", json={"vehicle_id": missing_id, "buyer_cpf": BUYER_CPF}).status_code == 404

    invalid_cpf = sales.post("/sales", json={"vehicle_id": 1, "buyer_cpf": "111.111.111-11"})
    assert invalid_cpf.status_code == 422

    unknown_payment = sales.post("/payments/webhook", json={"payment_code": "does-not-exist", "status": "paid"})
    assert unknown_payment.status_code == 404
