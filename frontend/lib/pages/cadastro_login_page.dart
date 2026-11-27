import 'package:google_fonts/google_fonts.dart';
import 'package:material_ui/material_ui.dart';
import 'package:muzzi_tennis/core/app_theme.dart';
import 'package:muzzi_tennis/widgets/app_navbar.dart';
import 'package:muzzi_tennis/widgets/campo_email.dart';
import 'package:muzzi_tennis/widgets/campo_senha.dart';
import 'package:muzzi_tennis/services/auth_service.dart';
import 'package:muzzi_tennis/widgets/warning_app_snackbar.dart';

class CadastroLoginPage extends StatefulWidget {
  const CadastroLoginPage({super.key});

  @override
  State<CadastroLoginPage> createState() => _CadastroLoginPageState();
}

class _CadastroLoginPageState extends State<CadastroLoginPage> {
  final _formKey = GlobalKey<FormState>();
  final _nomeController = TextEditingController();
  final _emailController = TextEditingController();
  final _telefoneController = TextEditingController();
  final _senhaController = TextEditingController();
  final _confirmarSenhaController = TextEditingController();
  final _authService = AuthService();
  bool _cadastrando = false;

  @override
  void dispose() {
    _nomeController.dispose();
    _emailController.dispose();
    _telefoneController.dispose();
    _senhaController.dispose();
    _confirmarSenhaController.dispose();
    super.dispose();
  }

  Future<void> _criarConta() async {
    if (_formKey.currentState?.validate() != true) {
      return;
    }

    setState(() {
      _cadastrando = true;
    });

    try {
      await _authService.registrarDono(
        nome: _nomeController.text,
        email: _emailController.text,
        telefone: _telefoneController.text,
        senha: _senhaController.text,
      );

      if (!mounted) return;

      AppSnackBar.sucesso(
        context,
        'Cadastro realizado com sucesso! Faça login.',
      );

      Navigator.pushNamedAndRemoveUntil(context, '/login', (route) => false);
    } catch (erro) {
      if (!mounted) return;

      final mensagem = erro.toString().replaceFirst('Exception: ', '');
      AppSnackBar.erro(context, mensagem);
    } finally {
      if (mounted) {
        setState(() {
          _cadastrando = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          const AppNavebar(),

          Expanded(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(
                  horizontal: 24,
                  vertical: 32,
                ),
                child: Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 450),
                    child: Form(
                      key: _formKey,
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text(
                            'CADASTRE-SE NO MUZZI TENNIS',
                            textAlign: TextAlign.center,
                            style: GoogleFonts.barlowCondensed(
                              fontSize: 32,
                              fontWeight: FontWeight.w900,
                              color: AppTheme.textoBranco,
                            ),
                          ),

                          TextFormField(
                            controller: _nomeController,
                            maxLength: 150,
                            textCapitalization: TextCapitalization.words,
                            decoration: const InputDecoration(
                              labelText: 'Nome completo',
                              hintText: 'Digite seu nome completo',
                              prefixIcon: Icon(Icons.person_outline),
                              border: OutlineInputBorder(),
                              counterText: '',
                            ),
                            validator: (valor) {
                              if (valor == null || valor.trim().isEmpty) {
                                return 'O nome completo é obrigatório.';
                              }
                              return null;
                            },
                          ),

                          const SizedBox(height: 20),
                          CampoEmail(
                            controller: _emailController,
                            maxLength: 150,
                            validator: (valor) {
                              if (valor == null || valor.trim().isEmpty) {
                                return 'O e-mail é obrigatório.';
                              }
                              final email = valor.trim();
                              final formatoEmail = RegExp(
                                r'^[^\s@]+@[^\s@]+\.[^\s@]+$',
                              );
                              if (!formatoEmail.hasMatch(email)) {
                                return 'Informe um e-mail válido.';
                              }
                              return null;
                            },
                          ),

                          const SizedBox(height: 20),
                          TextFormField(
                            controller: _telefoneController,
                            keyboardType: TextInputType.phone,
                            decoration: const InputDecoration(
                              labelText: 'Telefone (opcional)',
                              hintText: '(31) 99999-9999',
                              prefixIcon: Icon(Icons.phone_outlined),
                              border: OutlineInputBorder(),
                            ),
                            validator: (valor) {
                              if (valor == null || valor.trim().isEmpty) {
                                return null;
                              }
                              final telefone = valor.trim();
                              final caracteresPermitidos = RegExp(
                                r'^[0-9()+\s-]+$',
                              );
                              if (!caracteresPermitidos.hasMatch(telefone)) {
                                return 'O telefone contém caracteres inválidos.';
                              }
                              final numeros = telefone.replaceAll(
                                RegExp(r'\D'),
                                '',
                              );
                              if (numeros.length < 10 || numeros.length > 13) {
                                return 'Informe um telefone com 10 a 13 dígitos.';
                              }
                              return null;
                            },
                          ),

                          const SizedBox(height: 20),
                          CampoSenha(
                            controller: _senhaController,
                            maxLength: 128,
                            validator: (valor) {
                              if (valor == null || valor.isEmpty) {
                                return 'A senha é obrigatória.';
                              }
                              if (valor.trim().isEmpty) {
                                return 'A senha não pode conter apenas espaços.';
                              }
                              if (valor.length < 8) {
                                return 'A senha deve ter no mínimo 8 caracteres.';
                              }
                              if (valor.length > 128) {
                                return 'A senha deve ter no máximo 128 caracteres.';
                              }
                              return null;
                            },
                          ),

                          const SizedBox(height: 20),
                          CampoSenha(
                            controller: _confirmarSenhaController,
                            label: 'Confirmar senha',
                            maxLength: 128,
                            validator: (valor) {
                              if (valor == null || valor.isEmpty) {
                                return 'A confirmação de senha é obrigatória.';
                              }
                              if (valor != _senhaController.text) {
                                return 'As senhas não coincidem.';
                              }
                              return null;
                            },
                          ),

                          const SizedBox(height: 24),
                          SizedBox(
                            height: 52,
                            child: ElevatedButton.icon(
                              onPressed: _cadastrando ? null : _criarConta,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: AppTheme.verdeMuzziTennis,
                                foregroundColor: AppTheme.fundoPreto,
                                elevation: 0,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                textStyle: GoogleFonts.barlowCondensed(
                                  fontSize: 18,
                                  fontWeight: FontWeight.w700,
                                  letterSpacing: 1,
                                ),
                              ),
                              icon: _cadastrando
                                  ? const SizedBox(
                                      width: 20,
                                      height: 20,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                        color: AppTheme.fundoPreto,
                                      ),
                                    )
                                  : const Icon(Icons.person_add_outlined),

                              label: Text(
                                _cadastrando ? 'CADASTRANDO...' : 'CRIAR CONTA',
                              ),
                            ),
                          ),

                          const SizedBox(height: 24),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(
                                'Já possui uma conta?',
                                style: GoogleFonts.barlow(
                                  fontSize: 14,
                                  color: AppTheme.textoCinza,
                                ),
                              ),

                              const SizedBox(width: 8),

                              TextButton(
                                onPressed: () {
                                  Navigator.pushReplacementNamed(
                                    context,
                                    '/login',
                                  );
                                },
                                style: TextButton.styleFrom(
                                  foregroundColor: AppTheme.verdeMuzziTennis,
                                ),
                                child: Text(
                                  'Faça login',
                                  style: GoogleFonts.barlow(
                                    fontSize: 14,
                                    fontWeight: FontWeight.w700,
                                    decoration: TextDecoration.underline,
                                    decorationColor: AppTheme.verdeMuzziTennis,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
