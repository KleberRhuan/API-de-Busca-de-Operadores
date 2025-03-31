import random
import string
import urllib.parse

import pytest
from fastapi import status


class TestFuzzing:
    """Testes de fuzzing para verificar a robustez da API contra entradas inesperadas ou maliciosas"""

    @pytest.mark.parametrize(
        "param", ["search", "page", "page_size", "sort_field", "sort_direction"]
    )
    def test_parameter_fuzzing(self, client, param, configure_service_mocks):
        """Teste para verificar como a API lida com valores inesperados nos parâmetros"""
        # Gerar valores aleatórios e potencialmente problemáticos para testar
        fuzz_values = [
            None,
            "",
            "null",
            "undefined",
            "NaN",
            "Infinity",
            "-Infinity",
            "true",
            "false",
            "0",
            "-1",
            "99999999999999999999",
            "3.14159265359",
            "-3.14159265359",
            "0x100",
            "0b1010",
            "'",
            '"',
            "`",
            ";",
            "<script>alert(1)</script>",
            "SELECT * FROM users",
            "DROP TABLE operators",
            "() { :; }; echo vulnerable",
            "'.sleep(10).'",
            "%00",
            "%0A",
            "ñáéíóú",
            "日本語",
            "🔥💯👍",
            "1'.exec(sleep(3)).'1",
            "../../etc/passwd",
            random_string(1000),  # String muito longa
        ]

        for value in fuzz_values:
            # Criar parâmetros para a URL
            params = {"search": "teste"}  # Valor padrão para garantir requisição válida

            if value is not None:
                params[param] = value

            # Construir a URL
            url = f"/api/v1/operators?{urllib.parse.urlencode(params)}"

            try:
                # Fazer a requisição
                response = client.get(url)

                # A API não deve retornar erro 500 (erro não tratado)
                assert (
                    response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR
                ), f"API retornou erro 500 para valor '{value}' no parâmetro {param}"

                # Resposta deve ter formato JSON válido
                if response.status_code != status.HTTP_422_UNPROCESSABLE_ENTITY:
                    try:
                        response.json()
                    except Exception as e:
                        pytest.fail(
                            f"Resposta não é JSON válido para valor '{value}' no parâmetro {param}: {str(e)}"
                        )
            except Exception as e:
                pytest.fail(
                    f"Exceção não tratada para valor '{value}' no parâmetro {param}: {str(e)}"
                )

    def test_long_url_fuzzing(self, client, configure_service_mocks):
        """Teste para verificar como a API lida com URLs extremamente longos"""
        # Gerar uma search string muito longa
        long_search = "search=" + "a" * 2000

        # Fazer a requisição
        try:
            response = client.get(f"/api/v1/operators?{long_search}")

            # A API não deve retornar erro 500 (erro não tratado)
            assert (
                response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR
            ), "API retornou erro 500 para URL muito longa"
        except Exception as e:
            pytest.fail(f"Exceção não tratada para URL muito longa: {str(e)}")

    def test_special_characters_fuzzing(self, client, configure_service_mocks):
        """Teste para verificar como a API lida com caracteres especiais nos parâmetros"""
        # Lista de caracteres especiais para testar
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?\\`~"

        for char in special_chars:
            # Codificar o caractere para a URL
            encoded_char = urllib.parse.quote(char)
            encoded_search = f"teste{encoded_char}123"

            # Fazer a requisição
            try:
                response = client.get(f"/api/v1/operators?search={encoded_search}")

                # A API não deve retornar erro 500 (erro não tratado)
                assert (
                    response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR
                ), f"API retornou erro 500 para caractere especial '{char}'"
            except Exception as e:
                pytest.fail(
                    f"Exceção não tratada para caractere especial '{char}': {str(e)}"
                )

    def test_unicode_fuzzing(self, client, configure_service_mocks):
        """Teste para verificar como a API lida com caracteres Unicode"""
        # Lista de categorias Unicode para testar
        unicode_categories = [
            ("emojis", "😀😁😂🤣😃😄😅😆"),
            ("direita para esquerda", "السلام عليكم שלום עליכם"),
            ("asiáticos", "你好こんにちは안녕하세요"),
            ("acentos", "áéíóúàèìòùâêîôûãẽĩõũç"),
            ("símbolos", "♠♥♦♣★☆☢☣♲♻⚠⚡"),
            ("matemáticos", "∀∂∃∅∇∈∉∋∏∑√∝∞∧∨∩∪∫≈≠≡≤≥"),
        ]

        for category_name, chars in unicode_categories:
            # Codificar os caracteres para a URL
            encoded_chars = urllib.parse.quote(chars)

            # Fazer a requisição
            try:
                response = client.get(f"/api/v1/operators?search=teste{encoded_chars}")

                # A API não deve retornar erro 500 (erro não tratado)
                assert (
                    response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR
                ), f"API retornou erro 500 para caracteres Unicode '{category_name}'"
            except Exception as e:
                pytest.fail(
                    f"Exceção não tratada para caracteres Unicode '{category_name}': {str(e)}"
                )

    @pytest.mark.parametrize(
        "method", ["post", "put", "delete", "patch", "options", "head"]
    )
    def test_http_method_fuzzing(self, client, method, configure_service_mocks):
        """Teste para verificar como a API lida com diferentes métodos HTTP"""
        # Obter o método do cliente
        client_method = getattr(client, method)

        # Fazer a requisição
        try:
            response = client_method("/api/v1/operators")

            # A API deve retornar 405 Method Not Allowed para métodos não suportados
            # ou lidar graciosamente com o método
            assert (
                response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR
            ), f"API retornou erro 500 para método HTTP '{method.upper()}'"

            # Se for OPTIONS, aceitar tanto 200/204 quanto 405 (se não implementado)
            if method == "options":
                assert response.status_code in [
                    status.HTTP_200_OK,
                    status.HTTP_204_NO_CONTENT,
                    status.HTTP_405_METHOD_NOT_ALLOWED,
                ]

            # Os outros métodos devem retornar 405 Method Not Allowed
            elif method not in ["get", "head"]:
                assert (
                    response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
                ), f"API não retornou 405 para método HTTP não suportado '{method.upper()}'"
        except Exception as e:
            pytest.fail(
                f"Exceção não tratada para método HTTP '{method.upper()}': {str(e)}"
            )


# Função auxiliar para gerar strings aleatórias
def random_string(length):
    """Gera uma string aleatória do tamanho especificado"""
    chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(chars) for _ in range(length))
