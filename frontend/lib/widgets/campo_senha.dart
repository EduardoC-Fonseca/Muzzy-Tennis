
import 'package:material_ui/material_ui.dart';

class CampoSenha extends StatefulWidget {
  final TextEditingController controller;
  final String label;
  final String? Function(String?)? validator;
  final int? maxLength;

  const CampoSenha({
    super.key,
    required this.controller,
    this.label = 'Senha',
    this.validator,
    this.maxLength,
  });

  @override
  State<CampoSenha> createState() => _CampoSenhaState();
}

class _CampoSenhaState extends State<CampoSenha> {
  bool _senhaVisivel = false;

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: widget.controller,
      obscureText: !_senhaVisivel,
      enableSuggestions: false,
      autocorrect: false,
      maxLength: widget.maxLength,
      validator: widget.validator,
      decoration: InputDecoration(
        labelText: widget.label,
        hintText: 'Digite sua senha',
        prefixIcon: const Icon(Icons.lock_outline),
        border: const OutlineInputBorder(),
        counterText: '',
        suffixIcon: IconButton(
          tooltip: _senhaVisivel ? 'Ocultar senha' : 'Mostrar senha',
          icon: Icon(
            _senhaVisivel ? Icons.visibility_off_outlined : Icons.visibility_outlined,
          ),
          onPressed: () {
            setState(() {
              _senhaVisivel = !_senhaVisivel;
            });
          },
        ),
      ),
    );
  }
}
