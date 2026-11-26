import 'package:material_ui/material_ui.dart';

class CampoEmail extends StatelessWidget {
  final TextEditingController controller;
  final String? Function(String?)? validator;
  final int? maxLength;

  const CampoEmail({
    super.key,
    required this.controller,
    this.validator,
    this.maxLength,
  });

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      keyboardType: TextInputType.emailAddress,
      textInputAction: TextInputAction.next,
      maxLength: maxLength,
      validator: validator,
      decoration: const InputDecoration(
        labelText: 'E-mail',
        hintText: 'Digite seu e-mail',
        prefixIcon: Icon(Icons.email_outlined),
        border: OutlineInputBorder(),
        counterText: '',
      ),
    );
  }
}
