import 'package:material_ui/material_ui.dart';
import 'package:muzzi_tennis/widgets/app_navbar.dart';

class QuadrasPage extends StatelessWidget {
  const QuadrasPage({super.key});

  @override
  Widget build(BuildContext context) {
    final resultados = ModalRoute.of(context)?.settings.arguments as List<Map<String, Object>>?;

    return Scaffold(
      body: Column(
        children: [
          const AppNavebar(),
          if (resultados != null)
            Expanded(
              child: ListView(
                children: [
                  Text('Quadras encontradas: ${resultados.length}'),
                  if (resultados.isEmpty)
                    const ListTile(
                      title: Text('Nenhuma quadra encontrada.'),
                    ),
                  for (final quadra in resultados)
                    ListTile(
                      title: Text(quadra['nome'].toString()),
                      subtitle: Text(quadra['cidade'].toString()),
                    ),
                ],
              ),
            ),
          if (resultados == null)
            const Expanded(
              child: Center(
                child: Text('Página de Quadras'),
              ),
            ),
        ],
      ),
    );
  }
}