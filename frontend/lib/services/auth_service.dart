import 'dart:convert';

import 'package:http/http.dart' as http;

class AuthService {
  Future<void> login({required String email, required String senha}) async {
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
    if (resposta.statusCode == 403) {
      throw Exception('Acesso não permitido.');
    }
    if (resposta.statusCode != 204) {
      throw Exception(
        'Erro ao realizar login (HTTP ${resposta.statusCode}).',
      );
    }
  }

  Future<Map<String, dynamic>> obterUsuario() async {
    final url = Uri.base.resolve('/api/v1/auth/me');
    final resposta = await http.get(url);

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

  Future<String> obterTokenCsrf() async {
    final url = Uri.base.resolve('/api/v1/auth/csrf');
    final resposta = await http.get(url);

    if (resposta.statusCode == 401) {
      throw Exception('Sessão inválida ou expirada.');
    }

    if (resposta.statusCode != 200) {
      throw Exception(
        'Erro ao recuperar token CSRF (HTTP ${resposta.statusCode}).',
      );
    }

    final dados = jsonDecode(resposta.body);
    if (dados is! Map<String, dynamic>) {
      throw const FormatException(
        'Resposta CSRF inválida.',
      );
    }

    final tokenCsrf = dados['csrf_token'];
    if (tokenCsrf is! String || tokenCsrf.isEmpty) {
      throw const FormatException(
        'A API não retornou um token CSRF válido.',
      );
    }
    return tokenCsrf;
  }

  Future<void> logout() async {
    final tokenCsrf = await obterTokenCsrf();
    final url = Uri.base.resolve('/api/v1/auth/logout');
    final resposta = await http.post(
      url,
      headers: {
        'X-CSRF-Token': tokenCsrf,
      },
    );

    if (resposta.statusCode == 401) {
      throw Exception('Sessão inválida ou expirada.');
    }
    if (resposta.statusCode == 403) {
      throw Exception('Não foi possível validar a segurança da sessão.');
    }
    if (resposta.statusCode != 204) {
      throw Exception(
        'Erro ao encerrar sessão (HTTP ${resposta.statusCode}).',
      );
    }
  }
}
