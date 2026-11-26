import 'package:flutter/foundation.dart';

class AuthSession extends ChangeNotifier {
  AuthSession._();

  static final AuthSession instance = AuthSession._();

  String? _token;
  Map<String, dynamic>? _usuario;
  String? get token => _token;
  Map<String, dynamic>? get usuario => _usuario;
  bool get autenticado => _token != null && _usuario != null;

  void iniciarSessao({required String token, required Map<String, dynamic> usuario}) {
    _token = token;
    _usuario = Map.unmodifiable(usuario);
    notifyListeners();
  }

  void encerrarSessao() {
    _token = null;
    _usuario = null;
    notifyListeners();
  }
}
