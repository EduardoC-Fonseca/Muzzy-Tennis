import 'package:material_ui/material_ui.dart';
import 'package:muzzi_tennis/core/app_theme.dart';
import 'package:muzzi_tennis/pages/cadastro_login_page.dart';
import 'package:muzzi_tennis/pages/cadastro_quadras_page.dart';
import 'package:muzzi_tennis/pages/inicio_page.dart';
import 'package:muzzi_tennis/pages/login_page.dart';
import 'package:muzzi_tennis/pages/quadras_page.dart';
import 'package:muzzi_tennis/services/auth_session.dart';

void main() {
  runApp(const MuzziTennisApp());
}

class MuzziTennisApp extends StatefulWidget {
  const MuzziTennisApp({super.key});
  @override
  State<MuzziTennisApp> createState() => _MuzziTennisAppState();
}

class _MuzziTennisAppState extends State<MuzziTennisApp> {
  bool _restaurandoSessao = true;

  @override
  void initState() {
    super.initState();
    _restaurarSessao();
  }

  Future<void> _restaurarSessao() async {
    try {
      await AuthSession.instance.restaurarSessao();
    } 
    catch (_) {
    } 
    finally {
      if (mounted) {
        setState(() {
          _restaurandoSessao = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Muzzi Tennis',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.muzziTennisTheme,
      builder: (context, child) {
        return Stack(
          fit: StackFit.expand,
          children: [
            ?child,
            if (_restaurandoSessao)
              const ColoredBox(
                color: AppTheme.fundoPreto,
                child: Center(
                  child: CircularProgressIndicator(
                    color: AppTheme.verdeMuzziTennis,
                  ),
                ),
              ),
          ],
        );
      },

      home: const InicioPage(),
      routes: {
        '/quadras': (context) => const QuadrasPage(),
        '/cadastro-quadras': (context) => const CadastroQuadrasPage(),
        '/login': (context) => const LoginPage(),
        '/cadastro-login': (context) => const CadastroLoginPage(),
      },
    );
  }
}
