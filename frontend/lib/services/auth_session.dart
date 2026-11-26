import 'package:flutter/foundation.dart';

class AuthSession extends ChangeNotifier {
  AuthSession._();

  static final AuthSession instance = AuthSession._();

  Map<String, dynamic>? _usuario;
  Map<String, dynamic>? get usuario => _usuario;
  bool get autenticado => _usuario != null;

  void iniciarSessao({required Map<String, dynamic> usuario}) {
    _usuario = Map<String, dynamic>.unmodifiable(usuario);
    notifyListeners();
  }

  void encerrarSessao() {
    _usuario = null;
    notifyListeners();
  }
}
