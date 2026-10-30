import pytest

from app import app, calcular_nology_cashback


@pytest.mark.parametrize(
    ("valor", "desconto", "vip", "esperado"),
    [
        ("200.00", "0", False, "10.00"),
        ("200.00", "0", True, "11.00"),
        ("500.00", "0", False, "25.00"),
        ("501.00", "0", False, "50.10"),
        ("501.00", "0", True, "55.11"),
        ("100.00", "10", False, "4.50"),
        ("100.00", "100", True, "0.00"),
    ],
)
def test_calcular_nology_cashback(valor, desconto, vip, esperado):
    assert str(calcular_nology_cashback(valor, desconto, vip)) == esperado


@pytest.mark.parametrize(
    ("valor", "desconto"),
    [
        ("0", "0"),
        ("0.001", "0"),
        ("-10", "0"),
        ("100", "-1"),
        ("100", "100.01"),
        ("100", "abc"),
        ("NaN", "0"),
        ("Infinity", "0"),
        ("100000000", "0"),
    ],
)
def test_rejeita_entradas_invalidas(valor, desconto):
    with pytest.raises(ValueError):
        calcular_nology_cashback(valor, desconto, False)


@pytest.fixture
def cliente_api(monkeypatch):
    monkeypatch.setattr("app.DATABASE_URL", None)
    app.config.update(TESTING=True)
    return app.test_client()


def cabecalho_cliente():
    return {"X-Client-ID": "a" * 64}


def test_calcular_api_sem_banco_retorna_resultado_sem_persistir(cliente_api):
    resposta = cliente_api.post(
        "/calcular",
        json={"valor": 200, "desconto": 0, "tipo": "COMUM"},
        headers=cabecalho_cliente(),
    )

    assert resposta.status_code == 200
    dados = resposta.get_json()
    assert dados["cashback"] == "10.00"
    assert dados["persistido"] is False
    assert dados["aviso"]


def test_calcular_api_rejeita_json_invalido(cliente_api):
    resposta = cliente_api.post(
        "/calcular",
        data="não é json",
        content_type="text/plain",
        headers=cabecalho_cliente(),
    )

    assert resposta.status_code == 400
    assert "erro" in resposta.get_json()


def test_calcular_api_rejeita_tipo_desconhecido(cliente_api):
    resposta = cliente_api.post(
        "/calcular",
        json={"valor": 200, "desconto": 0, "tipo": "PREMIUM"},
        headers=cabecalho_cliente(),
    )

    assert resposta.status_code == 400


def test_calcular_api_exige_identificador_de_navegador(cliente_api):
    resposta = cliente_api.post(
        "/calcular",
        json={"valor": 200, "desconto": 0, "tipo": "COMUM"},
    )

    assert resposta.status_code == 400


def test_historico_informa_quando_banco_nao_esta_configurado(cliente_api):
    resposta = cliente_api.get("/historico", headers=cabecalho_cliente())

    assert resposta.status_code == 503
    assert "erro" in resposta.get_json()
