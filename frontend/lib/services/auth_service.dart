
import 'dart:convert';

import 'package:http/http.dart' as http;

class AuthService {
  Future<String> login({required String email, required String senha,}) async {
    final url = Uri.base.resolve('/api/v1/auth/login');

    final resposta = await http.post(
      url,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: {
        'username': email.trim(),
        'password': senha,
      },
    );

    if (resposta.statusCode == 401) {
      throw Exception('E-mail ou senha inválidos.');
    }
    if (resposta.statusCode != 200) {
      throw Exception(
        'Erro ao realizar login (HTTP ${resposta.statusCode}).',
      );
    }
    final dados = jsonDecode(resposta.body) as Map<String, dynamic>;
    final token = dados['access_token'];
    if (token is! String || token.isEmpty) {
      throw const FormatException(
        'A API não retornou um token de acesso válido.',
      );
    }
    return token;
  }

  Future<Map<String, dynamic>> obterUsuario(String token) async {
    final url = Uri.base.resolve('/api/v1/auth/me');

    final resposta = await http.get(
      url,
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (resposta.statusCode == 401) {
      throw Exception('Sessão inválida ou expirada.');
    }
    if (resposta.statusCode != 200) {
      throw Exception(
        'Erro ao buscar usuário (HTTP ${resposta.statusCode}).',
      );
    }
    final dados = jsonDecode(resposta.body);
    if (dados is! Map<String, dynamic>) {
      throw const FormatException(
        'A API retornou dados de usuário inválidos.',
      );
    }
    return dados;
  }

}
