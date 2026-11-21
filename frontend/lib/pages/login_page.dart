
import 'package:flutter_svg/flutter_svg.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:material_ui/material_ui.dart';
import 'package:muzzi_tennis/core/app_theme.dart';
import 'package:muzzi_tennis/widgets/app_navbar.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  bool senhaVisivel = false;

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
                    constraints: const BoxConstraints(
                      maxWidth: 920,
                    ),
                    child: Container(
                      padding: const EdgeInsets.all(40),
                      decoration: BoxDecoration(
                        color: AppTheme.superficiePreta,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: AppTheme.bordaPreta,
                          width: 1,
                        ),
                      ),

                      child: Row(
                        children: [
                          SizedBox(
                            width: 280,
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                SvgPicture.asset(
                                  'lib/assets/muzzi_logo.svg',
                                  width: 170,
                                  height: 170,
                                ),

                                const SizedBox(height: 20),
                                Text.rich(
                                  TextSpan(
                                    children: [
                                      TextSpan(
                                        text: 'MUZZI ',
                                        style: TextStyle(
                                          color: AppTheme.textoBranco,
                                        ),
                                      ),
                                      TextSpan(
                                        text: 'TENNIS',
                                        style: TextStyle(
                                          color:
                                              AppTheme.verdeMuzziTennis,
                                        ),
                                      ),
                                    ],
                                  ),
                                  style: GoogleFonts.barlowCondensed(
                                    fontSize: 36,
                                    fontWeight: FontWeight.w900,
                                    letterSpacing: 1,
                                  ),
                                ),
                              ],
                            ),
                          ),

                          const SizedBox(width: 32),
                          Container(
                            width: 1,
                            height: 320,
                            color: AppTheme.bordaPreta,
                          ),

                          const SizedBox(width: 32),
                          Expanded(
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              crossAxisAlignment:
                                  CrossAxisAlignment.stretch,
                              children: [
                                Text(
                                  'BEM-VINDO DE VOLTA',
                                  textAlign: TextAlign.center,
                                  style: GoogleFonts.barlowCondensed(
                                    fontSize: 32,
                                    fontWeight: FontWeight.w900,
                                    color: AppTheme.textoBranco,
                                  ),
                                ),

                                const SizedBox(height: 12),
                                Text(
                                  'Acesse sua conta para continuar.',
                                  textAlign: TextAlign.center,
                                  style: GoogleFonts.barlow(
                                    fontSize: 14,
                                    color: AppTheme.textoCinza,
                                  ),
                                ),

                                const SizedBox(height: 32),
                                TextFormField(
                                  keyboardType:
                                      TextInputType.emailAddress,
                                  decoration: InputDecoration(
                                    labelText: 'E-mail',
                                    hintText: 'Digite seu e-mail',
                                    prefixIcon:
                                        Icon(Icons.email_outlined),
                                    border: OutlineInputBorder(),
                                  ),
                                ),

                                const SizedBox(height: 20),
                                TextFormField(
                                  obscureText: !senhaVisivel,
                                  decoration: InputDecoration(
                                    labelText: 'Senha',
                                    hintText: 'Digite sua senha',
                                    prefixIcon:
                                        const Icon(Icons.lock_outline),
                                    border: const OutlineInputBorder(),
                                    suffixIcon: IconButton(
                                      tooltip: senhaVisivel ? 'Ocultar senha' : 'Mostrar senha',
                                      icon: Icon(
                                        senhaVisivel ? Icons.visibility_off_outlined : Icons.visibility_outlined,
                                      ),
                                      onPressed: () {
                                        setState(() {
                                          senhaVisivel = !senhaVisivel;
                                        });
                                      },
                                    ),
                                  ),
                                ),

                                const SizedBox(height: 24),
                                SizedBox(
                                  height: 52,
                                  child: ElevatedButton.icon(
                                    onPressed: () {
                                      debugPrint(
                                        'Botão de login pressionado',
                                      );
                                    },
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor:
                                          AppTheme.verdeMuzziTennis,
                                      foregroundColor:
                                          AppTheme.fundoPreto,
                                      elevation: 0,
                                      shape: RoundedRectangleBorder(
                                        borderRadius:
                                            BorderRadius.circular(8),
                                      ),
                                      textStyle:
                                          GoogleFonts.barlowCondensed(
                                        fontSize: 18,
                                        fontWeight: FontWeight.w700,
                                        letterSpacing: 1,
                                      ),
                                    ),
                                    icon: const Icon(Icons.login),
                                    label: const Text('ENTRAR'),
                                  ),
                                ),

                                const SizedBox(height: 24),
                                Wrap(
                                  alignment: WrapAlignment.center,
                                  crossAxisAlignment:
                                      WrapCrossAlignment.center,
                                  spacing: 4,
                                  children: [
                                    Text(
                                      'Quer anunciar e alugar suas quadras e ainda não possui cadastro?',
                                      style: GoogleFonts.barlow(
                                        fontSize: 14,
                                        color: AppTheme.textoCinza,
                                      ),
                                    ),

                                    TextButton(
                                      onPressed: () {
                                        Navigator.pushNamed(
                                          context,
                                          '/cadastro-login',
                                        );
                                      },
                                      style: TextButton.styleFrom(
                                        foregroundColor:
                                            AppTheme.verdeMuzziTennis,
                                        padding: EdgeInsets.zero,
                                        minimumSize: Size.zero,
                                        tapTargetSize:
                                            MaterialTapTargetSize
                                                .shrinkWrap,
                                      ),
                                      child: Text(
                                        'Cadastre-se aqui',
                                        style: GoogleFonts.barlow(
                                          fontSize: 14,
                                          fontWeight: FontWeight.w700,
                                          decoration:
                                              TextDecoration.underline,
                                          decorationColor:
                                              AppTheme.verdeMuzziTennis,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ],
                            ),
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
